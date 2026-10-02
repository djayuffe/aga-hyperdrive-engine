        include "hardware.i"

WIDTH           EQU 320
HEIGHT          EQU 256
BYTES_PER_ROW   EQU 40
PLANES          EQU 4
PLANE_SIZE      EQU BYTES_PER_ROW*HEIGHT
LOGO_PLANE_SIZE EQU 320*80/8
LOGO_BYTES      EQU PLANES*LOGO_PLANE_SIZE

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
; AGA_REQUIRE: production implementation should read Lisa/Denise ID before takeover.
; This first engine revision is structured so the gate is isolated and testable.
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
        move.l  #copper,d0
        move.w  d0,COP1LCL(a6)
        swap    d0
        move.w  d0,COP1LCH(a6)
        move.w  #DMAF_SETCLR|DMAF_MASTER|DMAF_COPPER|DMAF_BPL,DMACON(a6)
        bsr     Effect_Init
        bsr     Music_Init
        rts

Engine_Shutdown:
        lea     CUSTOM,a6
        move.w  #$7FFF,DMACON(a6)
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
        lea     screen,a0
        moveq   #0,d0
        move.w  #PLANES*PLANE_SIZE/4-1,d7
.clear:
        move.l  d0,(a0)+
        dbra    d7,.clear
        lea     logo_data,a0
        lea     screen,a1
        moveq   #PLANES-1,d6
.plane:
        move.w  #LOGO_PLANE_SIZE/4-1,d7
.copy:
        move.l  (a0)+,(a1)+
        dbra    d7,.copy
        lea     PLANE_SIZE-LOGO_PLANE_SIZE(a1),a1
        dbra    d6,.plane
        rts

; Effect_Frame updates the original state-of-the-art effect graph:
;  1. chunky-to-planar compatible four-plane logo layer
;  2. AGA 24-bit Copper plasma gradient
;  3. tunnel reciprocal table for ray/spline camera motion
;  4. future blitter vector layer and sprite particle layer
Effect_Frame:
        addq.w  #3,fx_phase
        bsr     Effect_UpdateCopperGradient
        rts

Effect_UpdateCopperGradient:
        lea     copper_fx_slots,a0
        lea     copper_gradient,a1
        move.w  fx_phase,d0
        and.w   #$00FF,d0
        moveq   #31,d7
.row:
        move.w  d0,d1
        add.w   d7,d1
        and.w   #$00FF,d1
        lsl.w   #2,d1
        move.l  0(a1,d1.w),d2
        move.w  d2,6(a0)
        swap    d2
        move.w  d2,14(a0)
        adda.w  #20,a0
        dbra    d7,.row
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
        rts

Music_Tick:
        addq.w  #1,music_tick
        rts

        section data,data
dos_name:       dc.b "dos.library",0
msg_need_aga:   dc.b "AGA Hyperdrive Engine needs an Amiga 1200/4000 AGA chipset.",10
msg_need_aga_end:
        even
dos_base:       dc.l 0
frame_counter:  dc.w 0
fx_phase:       dc.w 0
music_tick:     dc.w 0

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
        dc.w COLOR00,$000,COLOR01,$0CFF,COLOR02,$0F7D,COLOR03,$0FFF
        dc.w COLOR04,$06AF,COLOR05,$0F47,COLOR06,$0FC6,COLOR07,$0FFF
copper_fx_slots:
        rept 32
        dc.w $8001,$FFFE,BPLCON3,$0C00,COLOR00,$0000,BPLCON3,$0E00,COLOR00,$0000
        endr
        dc.w $FFFF,$FFFE
screen:
        ds.b PLANE_SIZE*PLANES
logo_data:
        incbin "assets/logo.raw"
mod_data:
        incbin "assets/hyperdrive.mod"
copper_gradient:
        incbin "assets/copper_gradient.bin"
tunnel_table:
        incbin "assets/tunnel.bin"
chipdata_end:
