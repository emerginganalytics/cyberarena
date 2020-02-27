# Pub/Sub Scripts
### This folder contains the code needed to run the pub/sub server

---
---
## [ validator.py ]:   
This script is what is used to test creation and deletion of Pub/Sub topics and subscribers.   
Not a final design -- Topic will be created upon workout build. No need to have a seperate
script to do the same thing.

---
## [ cg-post.py ]:   
This script can be used with any workout. In order for the script to work properly, you'll need to make
sure google-service.json file is downloaded on each machine. Modify the cg-post.py to point to the json
file location. 
  > Important to note mild syntax changes are to be made when implementing on Windows   
  > systems
  
Example workout publish calls:
  > python3 /<path to script/cg-post.py permissions 
---
