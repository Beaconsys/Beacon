#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<sys/types.h>
#include<sys/stat.h>
#include<fcntl.h>
#include"aggregation.h"

void compute(char*st,char*strtime,int *size,char*stroffset,char *keyword,char *address)
{
  char *strtmp,*strtmp1,*strtmp2;
  char strsize[15];
  int j;
  strncpy(strtime,st+1,19);
  strtime[19]='\0';
  if (strstr(strstr(st,keyword),"size"))
  {
    strtmp=strstr(strstr(st,keyword),"size");
    strtmp1=strstr(strtmp,"offset");
    strtmp2=strstr(strstr(st,keyword),"0x");
    j=5;
    while (strtmp[j]!=',') j++;
    strncpy(strsize,strtmp+5,j-5);
    strsize[j-5]='\0';
    *size=atoi(strsize);
    j=7;
    while (strtmp1[j]!=')') j++;
    strncpy(stroffset,strtmp1+7,j-7);
    stroffset[j-7]='\0';
    j=2;
    while (strtmp2[j]!=',') j++;
    strncpy(address,strtmp2,j);
    address[j]='\0';
  }
}

void agre(char *buf,int lines)
{
  char *st;
  char strtime[20];
  char cmptime[20];
  char address[30];
  char cmpress[30];
  char stroffset[30];
  char cmpoffset[30];
  int size;
  int sizeg;
  int count;
  int i;
  for (i=0;i<lines;i++)
  {
    st=buf + ( i * BUFSIZ);
    if ((!strchr(st,'['))||(strstr(st,"=>"))) continue;
    if ((strstr(st,"READ"))&&(strstr(strstr(st,"READ"),"size"))&&(strchr(st,'['))&&(!strstr(st,"READDIR")))
      {
        compute(st,strtime,&size,stroffset,"READ",address);
        strcpy(cmptime,strtime); 
        sizeg=size;
        strcpy(cmpress,address);
        strcpy(cmpoffset,stroffset);
        count=1;
        i+=1;
        st=buf + ( i * BUFSIZ);
        while (((!strchr(st,'['))||(strstr(st,"=>")))&&(i<lines-1))
        {
          i+=1;
          st=buf + (i*BUFSIZ);
         }
        while ((strstr(st,"READ"))&&(strstr(strstr(st,"READ"),"size"))&&(strchr(st,'['))&&(!strstr(st,"READDIR")))
        {
          compute(st,strtime,&size,stroffset,"READ",address);
          if ((!strcmp(strtime,cmptime))&&(!strcmp(address,cmpress))&&(size==sizeg)&&(atoi(cmpoffset)+size==atoi(stroffset)))
          {  
            strcpy(cmpoffset,stroffset);
            count+=1;
          }
          else
          {
            fprintf(stdout,"[%s] T %s %s size=%d offset=%s count=%d\n",cmptime,"READ",cmpress,sizeg,cmpoffset,count);
            strcpy(cmptime,strtime); 
            sizeg=size;
            strcpy(cmpress,address);
            strcpy(cmpoffset,stroffset);
            count=1;
          }
          if (i<lines-1)
          {
            i+=1;
            st=buf + ( i * BUFSIZ);
          }
          else break;
          while (((!strchr(st,'['))||(strstr(st,"=>")))&&(i<lines-1))
          {
            i+=1;
            st=buf + (i*BUFSIZ);
          }
        }
        if (count>0)
        {
            fprintf(stdout,"[%s] T %s %s size=%d offset=%s count=%d\n",cmptime,"READ",cmpress,sizeg,cmpoffset,count);
        }
        i-=1;
      }//end if READ
      else if ((strstr(st,"WRITE"))&&(strstr(strstr(st,"WRITE"),"size"))&&(strchr(st,'['))&&(!strstr(st,"WRITEDIR")))
      {
        compute(st,strtime,&size,stroffset,"WRITE",address);
        strcpy(cmptime,strtime); 
        sizeg=size;
        strcpy(cmpress,address);
        strcpy(cmpoffset,stroffset);
        count=1;
        i+=1;
        st=buf + ( i * BUFSIZ);
        while (((!strchr(st,'['))||(strstr(st,"=>")))&&(i<lines-1))
        {
          i+=1;
          st=buf + (i*BUFSIZ);
         }
        while ((strstr(st,"WRITE"))&&(strstr(strstr(st,"WRITE"),"size"))&&(strchr(st,'['))&&(!strstr(st,"WRITEDIR")))
        {
          compute(st,strtime,&size,stroffset,"WRITE",address);
          if ((!strcmp(strtime,cmptime))&&(!strcmp(address,cmpress))&&(size==sizeg)&&(atoi(cmpoffset)+size==atoi(stroffset)))
          {  
            strcpy(cmpoffset,stroffset);
            count+=1;
          }
          else
          {
            fprintf(stdout,"[%s] T %s %s size=%d offset=%s count=%d\n",cmptime,"WRITE",cmpress,sizeg,cmpoffset,count);
            strcpy(cmptime,strtime); 
            sizeg=size;
            strcpy(cmpress,address);
            strcpy(cmpoffset,stroffset);
            count=1;
          }
          if (i<lines-1)
          {
            i+=1;
            st=buf + ( i * BUFSIZ);
          }
          else break;
          while (((!strchr(st,'['))||(strstr(st,"=>")))&&(i<lines-1))
          {
            i+=1;
            st=buf + (i*BUFSIZ);
          }
        }
        if (count>0)
        {
            fprintf(stdout,"[%s] T %s %s size=%d offset=%s count=%d\n",cmptime,"WRITE",cmpress,sizeg,cmpoffset,count);
        }
        i-=1;
      }//end if WRITE
      else 
      {
         fputs(st,stdout);
      }
  }//end for

}//end function


void agregation(char *buf,int lines)
{
   agre(buf,lines);
}
#ifdef DC
int main(int argc,char **argv)
{
  char*filename;
  int lines;
  char *buf,*p;
  int tail=0;
  FILE *str;
  int i;
  if (argc<2) exit(0);
  filename=argv[1];
  str=fopen(filename,"r");
  buf=(char*)malloc(40000*BUFSIZ);
  
  p=buf;
  while(fgets(p,BUFSIZ,str))
  {
    tail++;
    p=buf+(tail*BUFSIZ);
  }
  printf("tail=%d \n",tail);
  agregation(buf,tail);
  fflush(stdout);
  free(buf);
  fclose(str);
  return 0;

}
#endif
