        include "hardware.i"

WIDTH           EQU 320
HEIGHT          EQU 256
BYTES_PER_ROW   EQU 40
PLANES          EQU 4
PLANE_SIZE      EQU BYTES_PER_ROW*HEIGHT
LOGO_PLANE_SIZE EQU 320*80/8
LOGO_BYTES      EQU PLANES*LOGO_PLANE_SIZE
AUDIO_WORDS     EQU 8287
SPRITE_HEIGHT   EQU 16
SPRITE_WORDS    EQU 2+SPRITE_HEIGHT*2+2
SPRITE_BYTES    EQU SPRITE_WORDS*2
VECTOR_BYTES    EQU BYTES_PER_ROW*64

        section code,code

_start:
        movem.l d0-d7/a0-a6,-(sp)
        bsr     Startup_OpenDOS
        bsr     Startup_AGAGate
        tst.w   d0
        bne     .ok
        bsr     Startup_PrintNeedAGA
        moveq   #20,d0
        bra     Exit
.ok:
        bsr     Engine_Init
.loop:
        bsr     Engine_WaitFrame
        bsr     Effect_Frame
        bsr     Music_Tick
        addq.w  #1,frame_counter
        btst    #6,CIAAPRA
        bne     .loop
        bsr     Engine_Shutdown
        moveq   #0,d0
Exit:
        movem.l (sp)+,d0-d7/a0-a6
        rts

Startup_OpenDOS:
        move.l  4.w,a6
        lea     dos_name,a1
        moveq   #0,d0
        jsr     LVOOpenLibrary(a6)
        move.l  d0,dos_base
        rts

Startup_AGAGate:
        lea     CUSTOM,a6
        move.w  DENISEID(a6),d0
        move.w  d0,chipset_id
        and.w   #$00FF,d0
        cmp.w   #$00F8,d0
        beq.s   .aga
        cmp.w   #$00FC,d0
        beq.s   .aga
        moveq   #0,d0
        rts
.aga:
        moveq   #1,d0
        rts

Startup_PrintNeedAGA:
        move.l  dos_base,d0
        beq.s   .done
        move.l  d0,a6
        jsr     LVOOutput(a6)
        move.l  d0,d1
        lea     msg_need_aga,a0
        move.l  a0,d2
        moveq   #msg_need_aga_end-msg_need_aga,d3
        jsr     LVOWrite(a6)
.done: rts

Engine_Init:
        lea     CUSTOM,a6
        bsr     Screen_Init
        bsr     Copper_Build
        bsr     Sprite_Build
        move.l  #copper,d0
        move.w  d0,COP1LCL(a6)
        swap    d0
        move.w  d0,COP1LCH(a6)
        move.w  #DMAF_SETCLR|DMAF_MASTER|DMAF_COPPER|DMAF_BPL|DMAF_SPRITE|DMAF_BLIT,DMACON(a6)
        bsr     Effect_Init
        bsr     Scene_Init
        bsr     Music_Init
        rts

Engine_Shutdown:
        lea     CUSTOM,a6
        move.w  #$7FFF,DMACON(a6)
        move.w  #0,AUD0VOL(a6)
        rts

Engine_WaitFrame:
        lea     CUSTOM,a6
.leave:
        move.w  VPOSR(a6),d0
        and.w   #$01FF,d0
        cmp.w   #300,d0
        bhs.s   .leave
.wait:
        move.w  VPOSR(a6),d0
        and.w   #$01FF,d0
        cmp.w   #300,d0
        blo.s   .wait
        rts

Effect_Init:
        clr.w   fx_phase
        rts

Screen_Init:
        bsr     Blitter_ClearVectorPlane
        rts

; Effect_Frame drives custom-chip work every PAL frame:
;  1. AGA 24-bit Copper colour lattice
;  2. runtime BPLCON1 scroll/shear warp
;  3. tunnel reciprocal camera/depth modulation
;  4. real hardware sprite-orb control words
;  5. blitter-maintained vector scratch plane
;  6. music event modulation
Effect_Frame:
        bsr     Scene_Update
        bsr     Music_EventBus
        bsr     Effect_CopperLattice
        bsr     Effect_BitplaneWarp
        bsr     Effect_TunnelLayer
        bsr     Effect_SpriteOrbLayer
        bsr     Effect_BlitterVectorPulse
        rts

Effect_BitplaneWarp:
        lea     CUSTOM,a6
        move.w  frame_counter,d0
        add.w   music_pulse,d0
        and.w   #$000F,d0
        move.w  d0,d1
        lsl.w   #4,d1
        or.w    d1,d0
        move.w  d0,BPLCON1(a6)
        rts

Effect_CopperLattice:
        lea     copper_fx_slots,a0
        lea     copper_gradient,a1
        move.w  fx_phase,d0
        add.w   scene_speed,d0
        add.w   music_pulse,d0
        move.w  d0,fx_phase
        and.w   #$00FF,d0
        moveq   #31,d7
.row:
        move.w  d0,d1
        add.w   d7,d1
        add.w   tunnel_phase,d1
        and.w   #$00FF,d1
        lsl.w   #2,d1
        move.l  0(a1,d1.w),d2
        move.w  d2,6(a0)
        swap    d2
        move.w  d2,14(a0)
        adda.w  #20,a0
        dbra    d7,.row
        rts

Effect_TunnelLayer:
        lea     tunnel_table,a0
        move.w  tunnel_phase,d0
        add.w   scene_tunnel,d0
        and.w   #$00BF,d0
        move.w  d0,tunnel_phase
        lsl.w   #1,d0
        move.w  0(a0,d0.w),tunnel_depth
        rts

Effect_SpriteOrbLayer:
        move.w  orb_phase,d0
        add.w   scene_orbs,d0
        add.w   music_pulse,d0
        and.w   #$00FF,d0
        move.w  d0,orb_phase
        lea     sprite_orbs,a0
        lea     sprite_path,a1
        moveq   #7,d7
.orb:
        move.w  d0,d1
        add.w   d7,d1
        add.w   d7,d1
        and.w   #$00FF,d1
        lsl.w   #2,d1
        move.w  0(a1,d1.w),d2            ; x
        move.w  2(a1,d1.w),d3            ; y
        bsr     Sprite_SetControl
        adda.w  #SPRITE_BYTES,a0
        add.w   #29,d0
        dbra    d7,.orb
        rts

Sprite_SetControl:
        move.w  d2,d4                    ; d2=x, d3=y, a0=sprite
        lsr.w   #1,d4
        and.w   #$00FF,d4
        move.w  d3,d5
        and.w   #$00FF,d5
        lsl.w   #8,d5
        or.w    d4,d5
        move.w  d5,(a0)
        move.w  d3,d5
        add.w   #SPRITE_HEIGHT,d5
        and.w   #$00FF,d5
        lsl.w   #8,d5
        btst    #0,d2
        beq.s   .xlow
        bset    #0,d5
.xlow:
        move.w  d5,2(a0)
        rts

Effect_BlitterVectorPulse:
        move.w  frame_counter,d0
        and.w   #$001F,d0
        bne.s   .done
        bsr     Blitter_ClearVectorPlane
.done:
        rts

Blitter_Wait:
        lea     CUSTOM,a6
.busy:
        btst    #14,DMACONR(a6)
        bne.s   .busy
        rts

Blitter_ClearVectorPlane:
        bsr     Blitter_Wait
        lea     CUSTOM,a6
        move.w  #$0100,BLTCON0(a6)
        move.w  #0,BLTCON1(a6)
        move.w  #$FFFF,BLTAFWM(a6)
        move.w  #$FFFF,BLTALWM(a6)
        move.w  #0,BLTDMOD(a6)
        move.l  #vector_plane,d0
        move.w  d0,BLTDPTL(a6)
        swap    d0
        move.w  d0,BLTDPTH(a6)
        move.w  #(64<<6)|(BYTES_PER_ROW/2),BLTSIZE(a6)
        rts

Scene_Init:
        clr.w   scene_index
        clr.w   scene_frame
        move.w  #3,scene_speed
        move.w  #1,scene_tunnel
        move.w  #2,scene_orbs
        rts

Scene_Update:
        addq.w  #1,scene_frame
        cmp.w   #256,scene_frame
        blo.s   .same
        clr.w   scene_frame
        addq.w  #1,scene_index
        and.w   #$0003,scene_index
.same:
        lea     scene_table,a0
        move.w  scene_index,d0
        mulu.w  #6,d0
        move.w  0(a0,d0.w),scene_speed
        move.w  2(a0,d0.w),scene_tunnel
        move.w  4(a0,d0.w),scene_orbs
        rts

Copper_Build:
        lea     screen,a0
        lea     copper_bplptrs,a1
        moveq   #PLANES-1,d7
.plane:
        move.l  a0,d0
        swap    d0
        move.w  d0,2(a1)
        swap    d0
        move.w  d0,6(a1)
        lea     PLANE_SIZE(a0),a0
        adda.w  #8,a1
        dbra    d7,.plane
        rts

Music_Init:
        clr.w   music_tick
        lea     CUSTOM,a6
        move.l  #audio_loop,d0
        move.w  d0,AUD0LCL(a6)
        swap    d0
        move.w  d0,AUD0LCH(a6)
        move.w  #AUDIO_WORDS,AUD0LEN(a6)
        move.w  #428,AUD0PER(a6)
        move.w  #48,AUD0VOL(a6)
        move.w  #DMAF_SETCLR|DMAF_MASTER|DMAF_AUD0,DMACON(a6)
        rts

Music_Tick:
        addq.w  #1,music_tick
        rts

Music_EventBus:
        move.w  music_tick,d0
        and.w   #$000F,d0
        bne.s   .decay
        move.w  #12,music_pulse
        rts
.decay:
        tst.w   music_pulse
        beq.s   .done
        subq.w  #1,music_pulse
.done:
        rts

Sprite_Build:
        lea     sprite_orbs,a0
        lea     cop_sprptrs,a1
        moveq   #7,d7
.spr:
        move.l  a0,d0
        swap    d0
        move.w  d0,2(a1)
        swap    d0
        move.w  d0,6(a1)
        lea     12(a0),a0
        adda.w  #8,a1
        dbra    d7,.spr
        rts

        section data,data
dos_name:       dc.b "dos.library",0
msg_need_aga:   dc.b "AGA Hyperdrive Engine needs an Amiga 1200/4000 AGA chipset.",10
msg_need_aga_end:
        even
dos_base:       dc.l 0
chipset_id:     dc.w 0
frame_counter:  dc.w 0
fx_phase:       dc.w 0
music_tick:     dc.w 0
music_pulse:    dc.w 0
scene_index:    dc.w 0
scene_frame:    dc.w 0
scene_speed:    dc.w 3
scene_tunnel:   dc.w 1
scene_orbs:     dc.w 2
tunnel_phase:   dc.w 0
tunnel_depth:   dc.w 0
orb_phase:      dc.w 0
scene_table:
        dc.w 2,1,1
        dc.w 3,2,2
        dc.w 5,3,4
        dc.w 8,5,6

sprite_path:
        incbin  "assets/sprite_path.bin"

plasma_palette:
        incbin  "assets/plasma_palette.bin"

        section chipdata,data_c
        cnop 0,4
copper:
        dc.w DIWSTRT,$2C81,DIWSTOP,$2CC1
        dc.w DDFSTRT,$0038,DDFSTOP,$00D0
        dc.w BPLCON0,$4200,BPLCON1,$0000,BPLCON2,$0000
        dc.w BPLCON3,$0C00,BPLCON4,$0011
 copper_bplptrs:
        dc.w BPL1PTH,0,BPL1PTL,0
        dc.w BPL2PTH,0,BPL2PTL,0
        dc.w BPL3PTH,0,BPL3PTL,0
        dc.w BPL4PTH,0,BPL4PTL,0
cop_sprptrs:
        dc.w SPR0PTH,0,SPR0PTL,0
        dc.w SPR1PTH,0,SPR1PTL,0
        dc.w SPR2PTH,0,SPR2PTL,0
        dc.w SPR3PTH,0,SPR3PTL,0
        dc.w SPR4PTH,0,SPR4PTL,0
        dc.w SPR5PTH,0,SPR5PTL,0
        dc.w SPR6PTH,0,SPR6PTL,0
        dc.w SPR7PTH,0,SPR7PTL,0
        dc.w COLOR00,$000,COLOR01,$0CFF,COLOR02,$0F7D,COLOR03,$0FFF
        dc.w COLOR04,$06AF,COLOR05,$0F47,COLOR06,$0FC6,COLOR07,$0FFF
copper_fx_slots:
        rept 32
        dc.w $8001,$FFFE,BPLCON3,$0C00,COLOR00,$0000,BPLCON3,$0E00,COLOR00,$0000
        endr
        dc.w $FFFF,$FFFE
screen:
        incbin "assets/screen.raw"
logo_data:
        incbin "assets/logo.raw"
mod_data:
        incbin "assets/hyperdrive.mod"
audio_loop:
        incbin "assets/audio_loop.raw"
copper_gradient:
        incbin "assets/copper_gradient.bin"
tunnel_table:
        incbin "assets/tunnel.bin"
sprite_orbs:
        incbin "assets/sprite_orbs.bin"
vector_plane:
        ds.b VECTOR_BYTES
chipdata_end:
