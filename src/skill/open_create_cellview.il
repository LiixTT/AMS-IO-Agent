
;; Tool to open or create cellView
procedure(openOrCreateCellView(lib cell view)
    let((cvId)
        ;; Check if library exists
        libId = ddGetObj(lib)
        unless(libId
            ;; Create library
            libId = dbCreateLib(lib)
            printf("Created library: %s\n" lib)
        )
        
        ;; Open or create cellView
        cvId = dbOpenCellViewByType(lib cell view "schematic" "a")
        when(cvId
            printf("CellView opened/created: %s/%s/%s\n" lib cell view)
            hiSetCurrentWindow(cvId)
        )
        cvId
    )
)

;; Execute
cv = openOrCreateCellView("LLM_Layout_Design" "IO_RING_8x8_double_ring_multi_voltage_domain" "schematic")
when(cv
    printf("Success! Current cellView: %L\n" cv)
    t
    printf("Failed to open/create cellView\n")
    nil
)
