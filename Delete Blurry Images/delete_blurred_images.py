import cv2
import os
import glob

def is_blurry(image_path, threshold=100):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    laplacian = cv2.Laplacian(image, cv2.CV_64F).var()  # Measure sharpness
    return laplacian < threshold

folder_path = "C:\DATA\Old OS\Bluetooth\Ilighter\WFDownloader"  # Change this to your folder

#for filename in os.listdir(folder_path):
for filename in glob.iglob(folder_path + '**/**', recursive=True):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path) and is_blurry(file_path):
        os.remove(file_path)  # Delete if blurry
        print(f"Deleted {filename}")

print("Finished deleting blurry images.")