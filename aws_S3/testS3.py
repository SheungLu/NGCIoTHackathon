import boto3
import pygame
import pygame.camera


pygame.camera.init()

cam = pygame.camera.Camera("/dev/video0",(640,480))
cam.start()
img = cam.get_image()
pygame.image.save(img,"webcam.jpg")

# Create an S3 client
s3 = boto3.client('s3')

filename = 'webcam.jpg'
bucket_name = 'aws-website-ngchackathonfiretruck-2w9yn'
key = 'images/'+filename
# Uploads the given file using a managed uploader, which will split up large
# files automatically and upload parts in parallel.
s3.upload_file(filename, bucket_name, key)
