import cv2
stream_url = "http://203.253.25.202:5000/stream?src=0"

cap = cv2.VideoCapture(stream_url)
if cap.isOpened():
	while True :
		ret, frame = cap.read() #성공적으로 이미지를 불러왔는지, 실제 이미지(프레임) 자체
		if ret :
			print(frame.shape) #해당 이미지의 해상도 print
			cv2.imshow("test",frame) #이미지를 윈도우 상에 출력
		else :
			print("failed to read frame")
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
else :
	print("can't open")
	
cv2.waitKey(0)
cv2.destroyAllWindows()