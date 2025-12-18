
;; Open a basic cellview to have a window open
libName = "basic"
cellName = "noConn"
viewName = "symbol"

cvId = dbOpenCellView(libName cellName viewName)
if(cvId then
    printf("Opened cellview %s/%s/%s\n" libName cellName viewName)
    geOpenCellView(cvId)
else
    printf("Failed to open basic cellview\n")
)
