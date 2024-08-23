import cv2

def __saliency(src):
    saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
    (success, saliemcy_map) = saliency.computeSaliency(src)
    if success is False:
        return (False, None)
    saliemcy_map = (saliemcy_map * 255).astype("uint8")
    heatmap = cv2.applyColorMap(saliemcy_map, cv2.COLORMAP_JET)
    # src1の重み0.7 src2の重み0.5 ガンマ1.0
    weight = cv2.addWeighted(src,0.7, heatmap ,0.5 ,1.0)
    return (success, weight)



def img_saliency(src_file = "sample3.png", dst_file = "sample_output3.png"):
    image = cv2.imread(src_file)
    saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
    (success, saliemcy_map) = __saliency(image)
    if success is True:
        cv2.imwrite(dst_file, saliemcy_map)


img_saliency()