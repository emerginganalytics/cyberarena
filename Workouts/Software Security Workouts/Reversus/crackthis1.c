#include<stdio.h>
#include<string.h>
#include<conio.h>

int main(){
	char str[15];
	
	printf("What's the validation code to the hacker machine?\n");
	gets(str);
	
	if(strcmp(str,"ABCD-1234-5678") == 0)
		printf("Access granted!\n");
	else
		printf("Access denied!\n");
	printf("Press any key to exit...\n");	
    getch();
	return 0;
	
}
