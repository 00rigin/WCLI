import cv2
import numpy as np

image = cv2.imread("arin.jpg", cv2.IMREAD_ANYCOLOR)
print(image.shape)
cv2.imshow("TEST", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
