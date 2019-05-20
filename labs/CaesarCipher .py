#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Caesar Cipher
MAX_KEY_SIZE = 26


# In[2]:


def getMode():
      while True:
          print('Do you wish to encrypt or decrypt a message? (e or d)')
          mode = input().lower()
          if mode in 'encrypt e decrypt d'.split():
             return mode
      else:
             print('Enter either "encrypt" or "e" or "decrypt" or "d".')


# In[10]:


def getMessage():
   if mode in ['e', 'en', 'enc', 'encr', 'encry','encrypt']:
          print('Enter the plaintext:')
   else:
          print('Enter the ciphertext: ')
   return input()


# In[11]:


def getKey():
     key = 0
     while True:
         print('Enter the key number (1-%s)' % (MAX_KEY_SIZE))
         key = int(input())
         if (key >= 1 and key <= MAX_KEY_SIZE):
             return key


# In[12]:


def getTranslatedMessage(mode, message, key):
     if mode[0] == 'd':
         key = -key
     translated = ''

     for symbol in message:
         if symbol.isalpha():
             num = ord(symbol)
             num += key

             if symbol.isupper():
                 if num > ord('Z'):
                     num -= 26
                 elif num < ord('A'):
                     num += 26
             elif symbol.islower():
                 if num > ord('z'):
                     num -= 26
                 elif num < ord('a'):
                     num += 26

             translated += chr(num)
         else:
             translated += symbol
     return translated


# In[15]:


mode = getMode()
message = getMessage()
key = getKey()

if mode in ['e', 'en', 'enc', 'encr', 'encry','encrypt']:
    print('The ciphertext is: ')
else:
    print('The plaintext is: ')
print(getTranslatedMessage(mode, message, key))


# In[ ]:




