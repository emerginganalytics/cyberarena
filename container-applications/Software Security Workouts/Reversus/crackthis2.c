#include<stdio.h>
#include<string.h>
#include<conio.h>

int main(){
	int x;
	
	printf("What's the valid code to obtain the flag?\n");
	scanf("%d", &x);
		
	if(x == 0xb1eed)
	{
		printf("Access granted!\n");
	}else{
		printf("Access denied!\n");
	}
	printf("Press any key to exit...");
	getch();
	return 0;
}