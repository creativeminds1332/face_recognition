from django.shortcuts import render
from gtts import gTTS
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
import time
from .models import face_dataset
from .models import Unknown_dataset
from .models import unrecognized
import shutil
import dlib
import numpy as np
import os
import cv2
import pickle
import face_recognition
import datetime
from django.db.models import Q
from django.views.decorators import gzip
from django.views.decorators.csrf import csrf_exempt
import pygame
import sys
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from PIL import Image



#global variables
path='C:\\Users\\HP\\Desktop\\5B\\PROJECT\\face_recognition\\dataset'
homepath='C:\\Users\\HP\\Desktop\\5B\\PROJECT\\face_recognition\\home_surveillance\\security_camera\\static\\security_camera\\Unknown'
class_names =[]

name_encodings_dict={}
VALID_EXTENSIONS = ['.png', '.jpg', '.jpeg']
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")
face_encoder = dlib.face_recognition_model_v1("models/dlib_face_recognition_resnet_model_v1.dat")



def face_rects(image):
    # convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # detect faces in the grayscale image
    rects = face_detector(gray, 1)
    # return the bounding boxes
    return rects

def face_landmarks(image):
    return [shape_predictor(image, face_rect) for face_rect in face_rects(image)]

def face_encodings(image):
    # compute the facial embeddings for each face 
    # in the input image. the `compute_face_descriptor` 
    # function returns a 128-d vector that describes the face in an image

    return [np.array(face_encoder.compute_face_descriptor(image, face_landmark))
            for face_landmark in face_landmarks(image)]

def nb_of_matches(known_encodings, unknown_encoding):
    # compute the Euclidean distance between the current face encoding 
    # and all the face encodings in the database
    distances = np.linalg.norm(known_encodings - unknown_encoding, axis=1)
    # keep only the distances that are less than the threshold
    small_distances = distances <= 0.45
    # return the number of matches
    k=(sum(small_distances))
    # print(k)
    return sum(small_distances)



def homepage(request):
    cards=face_dataset.objects.all().order_by('-reg_date')
    count=face_dataset.objects.count()
    serialkey=unrecognized.objects.all().order_by('-cap_date')
    context={'cards':cards, 'count':count,'serialkey':serialkey}
    return render(request, 'security_camera/homepage.html', context)

def register(request):
    return render(request, 'security_camera/homepage.html')

def search(request):
    if request.method=='POST':
        try:
            user_name=request.POST['searchname']
            cards=face_dataset.objects.filter(Q(firstname__icontains=user_name) | Q(secondname__icontains=user_name))
            count=face_dataset.objects.count()
            context={'cards':cards, 'count':count}
            return render(request, 'security_camera/homepage.html', context)
        except:
            return HttpResponseRedirect(reverse('security_camera:homepage', ))
        
    return render(request, 'security_camera/homepage.html', context)

def update(request):
    if request.method =='POST':

        personel=face_dataset.objects.get(pk=request.POST['PersonId'])
        with open("C:\\Users\\HP\Desktop\\5B\PROJECT\\face_recognition\\dataset\\encodings.pickle", "rb") as f:
            encodings_database = pickle.load(f)
            encodings_database[request.POST['FirstName'] + ' ' + request.POST['SecondName']] = encodings_database.pop(personel.firstname + ' ' + personel.secondname)

        with open("C:\\Users\\HP\Desktop\\5B\PROJECT\\face_recognition\\dataset\\encodings.pickle", "wb") as f:
            pickle.dump(encodings_database, f)

        old_filename=personel.firstname + '_' + personel.secondname
        new_filename=request.POST['FirstName'] + '_' + request.POST['SecondName']
        old_path = os.path.join(path, old_filename)
        new_path = os.path.join(path, new_filename)

        # Rename the file
        shutil.move(old_path, new_path)
        #update database
        personel.firstname=request.POST['FirstName']
        personel.secondname=request.POST['SecondName']
        personel.title=request.POST['Title']
        personel.save()
       
        return HttpResponseRedirect(reverse('security_camera:homepage', ))

def viewpic(request):
    if request.method=="POST":
        filename=request.POST['serial_no']
        # Open the image file
        image = Image.open(homepath+'\\'+ filename + '.jpg')

        # Show the image
        image.show()
        return HttpResponseRedirect(reverse('security_camera:homepage', ))


def delete(request):
    if request.method=='POST':
        first_target=request.POST['First_Name']
        second_target=request.POST['Second_Name']
        key=request.POST['identifier']
        face_dataset.objects.get(pk=key).delete()
        with open("C:\\Users\\HP\Desktop\\5B\PROJECT\\face_recognition\\dataset\\encodings.pickle", "rb") as f:
            encodings_database = pickle.load(f)
            del encodings_database[first_target + ' '  + second_target] 

        with open("C:\\Users\\HP\Desktop\\5B\PROJECT\\face_recognition\\dataset\\encodings.pickle", "wb") as f:
            pickle.dump(encodings_database, f)
        shutil.rmtree(path + '\\' + first_target + '_'  + second_target)
        return HttpResponseRedirect(reverse('security_camera:homepage'))
        
        
    else:
    
        return HttpResponseRedirect(reverse('security_camera:homepage'))
 



def webcam_feed(request):
    
    
    return render(request, 'security_camera/webcam_feed.html')
    

def upload(request):
    if request.method=='POST':
        FirstName=request.POST['FirstName']
        SecondName=request.POST['SecondName']
        Title=request.POST['Title']
        uploadfile=request.FILES['image']
        username = FirstName + '_' + SecondName
        new=face_dataset.objects.create(firstname=FirstName, secondname=SecondName, title=Title)
        faces=face_dataset.objects.all()
        class_names.clear()
        for face in faces:
            class_names.append(face.firstname + face.secondname)
        
        # print(class_names)
        # print(uploadfile.size)
        # print(uploadfile.name)
        
        fs=FileSystemStorage()
        fs.save(uploadfile.name,uploadfile)
        os.chdir(path)
        New_folder=username
        os.makedirs(New_folder)
        file_path='C:\\Users\\HP\\Desktop\\5B\\PROJECT\\face_recognition\\home_surveillance\\dataset\\' + uploadfile.name
        dir_path=path +'\\'+ New_folder
        shutil.move(file_path, dir_path)
        print(class_names)
        # 
        images_path=dir_path +'\\' + uploadfile.name
        print(images_path)
        image=cv2.imread(images_path)
        encodings=face_encodings(image)
        if encodings:
            name=username.replace('_', " ")
            # get the encodings for the current name
            # e = name_encodings_dict.get(name, [])
            # # update the list of encodings for the current name
            # e.extend(encodings)
            # # update the list of encodings for the current name
            name_encodings_dict[name] = encodings
            print(encodings)
            # with open("encodings.pickle", "wb") as f:
            #     pickle.dump(name_encodings_dict, f)
            #     print('dictionary saved successfully to file')

            try:
                with open("encodings.pickle", "rb") as f:
                    person=pickle.load(f)
                    person[name] = encodings
                
                with open("encodings.pickle", "wb") as f:
                        pickle.dump(person, f)
                        print('dictionary saved successfully to file')

                with open("encodings.pickle", "rb") as f:
                        person=pickle.load(f)
                        print('Person dictionary')
                        print(person)
                
            except:

                with open("encodings.pickle", "wb") as f:
                    pickle.dump(name_encodings_dict, f)
                    print('dictionary saved successfully to file')

                with open("encodings.pickle", "rb") as f:
                        details = pickle.load(f)
                        print('Person dictionary')
                        print(details)
        else:
            shutil.rmtree( path + '\\' + username)
            face_dataset.objects.get(pk=new.id).delete()
            return HttpResponseRedirect(reverse('security_camera:homepage', ))
        
    return HttpResponseRedirect(reverse('security_camera:homepage', ))


def recognize(request):
    try:
        with open("C:\\Users\\HP\Desktop\\5B\PROJECT\\face_recognition\\dataset\\encodings.pickle", "rb") as f:
            encodings_database = pickle.load(f)
    except:
        return HttpResponseRedirect(reverse('security_camera:homepage', ))
        
        
    
    #image = cv2.imread("C:\\Users\\HP\\Pictures\\Camera Roll\\WIN_20230217_09_10_38_Pro.jpg")
    
    cam = cv2.VideoCapture(0)
    process_this_frame = True
    # cam.set(3, 640) # set video widht
    # cam.set(4, 480) # set video height
    # Define min window size to be recognized as a face
    # minW = 0.1*cam.get(3)
    # minH = 0.1*cam.get(4)
    duration =5
    # Get the start time
    start_time = cv2.getTickCount()
    while True:
        _,img =cam.read()
        small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        if process_this_frame:
            # get the 128-d face embeddings for each face in the input image
            encodings = face_encodings(img)
            # this list will contain the names of each face detected in the image
            names = []
            for encoding in encodings:
                # initialize a dictionary to store the name of the 
                # person and the number of times it was matched
                counts = {}
            
                # loop over the known encodings
                for (name, d_encodings) in encodings_database.items():
                    # compute the number of matches between the current encoding and the encodings 
                    # of the known faces and store the number of matches in the dictionary
                    counts[name] = nb_of_matches(d_encodings, encoding)
                    # check if all the number of matches are equal to 0
                    # if there is no match for any name, then we set the name to "Unknown"

                if all(count == 0 for count in counts.values()):
                    name = "Unknown"
                    names.append(name)
                    # otherwise, we get the name with the highest number of matches
                else:
                    name = max(counts, key=counts.get)
    
                    # add the name to the list of names
                    names.append(name)
                    # loop over the `rectangles` of the faces in the 
                    # input image using the `face_rects` function

        process_this_frame = not process_this_frame


        for rect, name in zip(face_rects(img), names):
            # get the bounding box for each face using the `rect` variable
            x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
            # draw the bounding box of the face along with the name of the person
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, name.replace('_', " "), (x1, y1 - 10), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        cv2.imshow('camera',img) 
        # Calculate the elapsed time (in seconds)
        elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()

         # Check if the duration has been reached
        if elapsed_time >= duration:
            
            try:
            
                if name=="Unknown":
                   
                    elapsed=int(time.time())
                    now = datetime.datetime.now()
                    capture_time=now.strftime("%I:%M %p")
                    unrecognized.objects.create(serial_no=elapsed)
                    
                    formatted_date_time = now.strftime("%m/%d/%Y %H:%M:%S")
                    cv2.imwrite(homepath + '\\' + str(elapsed) +'.jpg', img)
                    

                    # Create an Image object in the database
                   
                    # Associate the image file with the Image object
                    with open('C:\\Users\\HP\\Desktop\\5B\\PROJECT\\face_recognition\\home_surveillance\\security_camera\\static\\security_camera\\Unknown\\1.jpg', 'rb') as f:
                        Unknown_dataset.objects.create(image=f)
                    break
                else:
                    break
            except:
                break
        # Wait for a key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        

         
    # Do a bit of cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
    
    flag=2
    for nameitems in names:
        try:
            if nameitems =='Unknown':
                flag=1
                break
            else:
                flag=0
            
        except:
            
            pass
    currentTime = datetime.datetime.now()
    currentTime.hour
    if currentTime.hour < 12:
        session="Good Morning"
    elif 12 <= currentTime.hour < 18:
        session="Good Afternoon"
    else:
        session="Good Evening"

    if flag==1:

        pygame.init()
        pygame.mixer.init()

        # Load the alarm sound file
        
        alarm_sound = pygame.mixer.Sound("C:\\Users\\HP\\Desktop\\5B\\PROJECT\\face_recognition\\dataset\\audio\\emergency-alarm-with-reverb-29431.mp3")
        start_time = time.time()
        state=True
        # Play the sound repeatedly
        while state:
            if time.time() - start_time <= 4:
                alarm_sound.play()
                pygame.time.wait(5000)
            else:
                state=False
            identity=unrecognized.objects.get(serial_no=elapsed)
        try:
            mail=EmailMessage('UNRECOGNIZED FACE', 'Greetings! This is security notification for an unrecognized person in your premise which was picked up by the system at the time ' + capture_time + '. Attached is a capture that was taken as a security measure.', settings.EMAIL_HOST_USER, ['imbwaga@students.uonbi.ac.ke'])
        
            image_datapath= homepath + '\\' + str(elapsed) +'.jpg'
            mail.attach_file(image_datapath)
            mail.send()
            identity.status=1
            identity.save()
            
        except:
            pass
            
    if flag==0:

        try:
            import os
            mytext = "hello,This is,"+ str(*names) 
            audio = gTTS(text=mytext, lang="en", slow=False)
            audio.save("C:\\Users\\HP\\Desktop\\5B\\PROJECT\\face_recognition\\dataset\\example.mp3")
            pygame.init()
            pygame.mixer.init()
            feedback=pygame.mixer.Sound("C:\\Users\\HP\\Desktop\\5B\\PROJECT\\face_recognition\\dataset\\example.mp3")
            feedback.play()
        except:
            pass
            
    if flag==2:
        try:
            import os
            mytext = "No face detected" 
            audio = gTTS(text=mytext, lang="en", slow=False)
            audio.save("C:\\Users\\HP\\Desktop\\5B\\PROJECT\\face_recognition\\dataset\\example.mp3")
            pygame.init()
            pygame.mixer.init()
            feedback=pygame.mixer.Sound("C:\\Users\\HP\\Desktop\\5B\\PROJECT\\face_recognition\\dataset\\example.mp3")
            feedback.play()
            
        except:
            pass

    
            
    return HttpResponseRedirect(reverse('security_camera:homepage', ))

