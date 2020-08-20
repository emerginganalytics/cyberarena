/*

Lab: Simple Buffer Overflow PoC
Author: Ryan Ronquillo
Date: 6/19/2019

*/

#include <stdio.h>
#include <string.h>

int main()
{
    char password[20];
    int passcheck = 0;

    printf("\nWhat's the password?\n");
    gets(password);

    if(strcmp(password, "notapassword"))
    {
        printf("\nIncorrect password.\n");
    }
    else
    {
        printf("\nCorrect Password\n");
        passcheck = 1;
    }
    if(passcheck)
    {
        system("sudo /bin/sh");
    }
    return 0;
}
