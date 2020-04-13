#include<stdio.h>
#include<string.h>
#include<conio.h>

int check(char *Str1, char *Str2)
{
	int i = 0;
  	while(Str1[i] == Str2[i])
  	{
  		if(Str1[i] == '\0' && Str2[i] == '\0')
	  		break;
		i++;
	}
}	
void encrypt(char inpString[]) 
{   
    char theValue = 'N'; 
  
    int len = strlen(inpString); 
  
    for (int i = 0; i < len; i++) 
    { 
        inpString[i] = inpString[i] ^ theValue; 
    } 
} 
int main() 
{ 
    char encodedValue[] = "=+-<+:>/==9!<*"; 
	char storeValue[20];
	printf("What's the valid authentication code? \n");
	gets(storeValue);
	
	encrypt(encodedValue);
	if (!check(storeValue, encodedValue)){
		printf("Access granted!\n");
	}else{
		printf("Access denied!\n");
	}
    printf("Press any key to exit...\n");
	getch();
    return 0; 
} 