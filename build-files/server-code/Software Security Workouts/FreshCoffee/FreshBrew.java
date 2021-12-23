// Created For: UA Little Rock Cyber Gym
// Date: 09-28-2020 
// Author: Andrew Bomberger
import java.lang.StringBuilder;

public class FreshBrew {
    public static void main(String args[]){
        for(int var1 = 86000; var1 > 0; --var1) {
            try {
                Thread.sleep(1000L);
            } catch (Exception var6) {
            }
            coffee_cup(var1);
        }
        percolator();
    }
    public static void coffee_cup(Integer brewTime){
        System.out.printf("\n _________________________________\n");
        System.out.printf("(_________________________________)____\n");
        System.out.printf("|*********************************|__) )\n");
        System.out.printf("|*********************************|  )  )\n");
        System.out.printf("|---------------------------------|__) )\n");
        System.out.printf("|+++++++++++++++++++++++++++++++++|___)\n");
        System.out.printf(" \\+++++++++++++++++++++++++++++++/\n");
        System.out.printf("  \\-----------------------------/\n");
        System.out.printf("   \\___________________________/\n");
        System.out.printf("    (__________________________)\n");
        System.out.printf(" ======================================\n");
        System.out.printf(" **************************************\n");
        System.out.printf("\r%d seconds until you get coffee...\n\n\n\n\n\n\n\n\n\n\n\n", brewTime);
    }

    public static void percolator() {
        String[] coffee_beans = {"07B49206", "C6F7665207468", "796D2", "65206A6176", "61206A6976", "E6420697", "43796", "6F7665","4206C", "6520616", "73206D657D","2657247"};

        String ground_coffee = coffee_beans[6] + coffee_beans[11] + coffee_beans[2] + coffee_beans[0] + coffee_beans[1] + coffee_beans[3] + coffee_beans[4] + coffee_beans[4] + coffee_beans[9] + coffee_beans[5] + coffee_beans[8] + coffee_beans[7] + coffee_beans[10];

        StringBuilder output = new StringBuilder();
        for (int k = 0; k < ground_coffee.length(); k+=2) {
            String str = ground_coffee.substring(k, k+2);
            output.append((char)Integer.parseInt(str, 16));
        }
        System.out.println(output);
    }
}