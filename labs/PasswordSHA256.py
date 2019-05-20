#!/usr/bin/env python
# coding: utf-8

# In[2]:


from Crypto.Hash import SHA256
h = SHA256.new()
h.update(b'Hello')
h.update(b'Hello3476849asj')
print(h.hexdigest())


# In[ ]:




