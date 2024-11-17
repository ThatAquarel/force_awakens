import time
import ngrok
import qrcode
import matplotlib.pyplot as plt


listener = ngrok.connect(8080, authtoken="1Vyt9lxRBcSKnJwhyyMQFBvx0oX_71Cx7symZQqKxxyFaDEh8")

# Output ngrok url to console
print(f"Ingress established at {listener.url()}")

img = qrcode.make(listener.url())
plt.imshow(img)
plt.show()
