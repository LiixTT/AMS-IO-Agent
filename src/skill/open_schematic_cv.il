
;; Open or create a schematic cellview in a window
;; Usage: open_schematic_cv("IO_RING", "io_ring_schematic")
procedure(open_schematic_cv(lib cell)
    let((cv)
        ; Check if library exists
        unless(ddGetObj(lib)
            ; Create library if doesn't exist
            ddCreateLib(lib "tphn28hpcpgv18" "s" "w")
        )
        ; Open or create schematic cellview
        cv = schOpenCellView(lib cell "schematic" nil "a")
        ; Return cellview id
        cv
    )
)
;; Call the procedure
open_schematic_cv("IO_RING", "io_ring_schematic")
