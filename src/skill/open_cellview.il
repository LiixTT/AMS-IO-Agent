
;; Open or create a cellview
libName = "LLM_Layout_Design"
cellName = "IO_RING_12x12"
viewName = "schematic"

;; Check if library exists
libId = ddGetObj(libName)
if(libId then
    ;; Library exists
    cvId = dbOpenCellView(libName cellName viewName)
    if(cvId then
        printf("Opened existing cellview %s/%s/%s\n" libName cellName viewName)
    else
        ;; Create new
        cvId = dbCreateCellView(libName cellName viewName)
        printf("Created new cellview %s/%s/%s\n" libName cellName viewName)
    )
    geOpenCellView(cvId)
else
    ;; Create library
    libId = dbCreateLib(libName)
    cvId = dbCreateCellView(libName cellName viewName)
    printf("Created library and cellview %s/%s/%s\n" libName cellName viewName)
    geOpenCellView(cvId)
)
