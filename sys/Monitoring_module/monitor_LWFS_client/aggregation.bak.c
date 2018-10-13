#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<sys/types.h>
#include<sys/stat.h>
#include<fcntl.h>
#include"aggregation.h"
#include <math.h>
double cov(int *value,int len,double average)
{
  double col=0.0;
  int i;
  for (i=0;i<len;i++)
    col=col+pow(value[i]-average,2);
  col/=len;
  col=sqrt(col);
  return col;
}

void compute(char*st,char*strtime,int *size,char*stroffset,char *keyword)
{
  char *strtmp,*strtmp1;
  char strsize[15];
  int j;
  strncpy(strtime,st+1,19);
  strtime[19]='\0';
  if (strstr(strstr(st,keyword),"size"))
  {
    strtmp=strstr(strstr(st,keyword),"size");
    strtmp1=strstr(strtmp,"offset");
    j=5;
    while (strtmp[j]!=',') j++;
    strncpy(strsize,strtmp+5,j-5);
    strsize[j-5]='\0';
    j=7;
    while (strtmp1[j]!=')') j++;
    strncpy(stroffset,strtmp1+7,j-7);
    stroffset[j-7]='\0';
    *size=atoi(strsize);
  }
}

void agre(char *buf,int lines,char *keyword,int *fg)
{
  char *st;
  char keyp[20];
  char strtime[20];
  char cmptime[20];
  char stroffset[30];
 // char cmpoffset[30];
  int size;
  long long sumsize=0;
  int i,maxsize,minsize;
  int flag=1;
  int count=0;
  double average=0.0;
  int value[1011];
  double covl;
 /* 
  strcpy(keyp,keyword);
  keyp[strlen(keyword)+0]='D';
  keyp[strlen(keyword)+1]='I';
  keyp[strlen(keyword)+2]='R';
  keyp[strlen(keyword)+3]='\0';
*/
  strcpy(keyp,keyword);
  strcat(keyp,"DIR");
//  fputs(keyp,stdout);
  for (i=0;i<lines;i++)
  {
    st=buf + ( i * BUFSIZ);
   if ((strstr(st,keyword))&&(strstr(strstr(st,keyword),"size"))&&(strchr(st,'['))&&(flag)&&(!strstr(st,keyp)))
    { 
      compute(st,strtime,&size,stroffset,keyword);
      sumsize=size;
      minsize=size;
      maxsize=size;
      strcpy(cmptime,strtime);
//      fprintf(stdout,"i=%d cmptime=%s strtime=%s\n",i,cmptime,strtime);
      value[count]=size;
      count=1;
      flag=0;
    }
   else if ((strstr(st,keyword))&&(strstr(strstr(st,keyword),"size"))&&(strchr(st,'['))&&(!flag)&&(!strstr(st,keyp)))
    {
      compute(st,strtime,&size,stroffset,keyword);
      if (!strcmp(strtime,cmptime)) 
      {
        sumsize+=size;
        value[count]=size;
        if (size<minsize) minsize=size;
        if (size >maxsize) maxsize=size;
        count++;
      }
      else if (strcmp(strtime,cmptime))
      {
        if (count>0)
        {
/*
          fputs("[",stdout);
          fputs(cmptime,stdout);
          fputs("] T ",stdout);
          fputs(keyword,stdout);
          fputs(" size=",stdout);
          fprintf(stdout,"%lld",sumsize);
          fputs(" count=",stdout);
          fprintf(stdout,"%d\n",count);
*/        average=sumsize/count;
          covl=cov(value,count,average);
          fprintf(stdout,"[%s] T %s size=%lld count=%d maxsize=%d minsize=%d average=%.2lf cov=%.2lf\n",cmptime,keyword,sumsize,count,maxsize,minsize,average,covl);
      }
        sumsize=size;
        minsize=size;
        maxsize=size;
        strcpy(cmptime,strtime);
//        fprintf(stdout,"i=%d cmptime=%s strtime=%s\n",i,cmptime,strtime);
        value[0]=size;
        count=1;
        flag=0;
      }
    }
  else if ((strstr(st,"OPEN"))&&(strchr(st,'[')))
    {
      if (*fg)
      {
        fputs(st,stdout);
        *fg=*fg+1;
      }
      if (count>0)
      {
/*
        fputs("[",stdout);
        fputs(cmptime,stdout);
        fputs("] T ",stdout);
        fputs(keyword,stdout);
        fputs(" size=",stdout);
        fprintf(stdout,"%lld",sumsize);
        fputs(" count=",stdout);
        fprintf(stdout,"%d\n",count);
*/
        average=sumsize/count;
        covl=cov(value,count,average);
        fprintf(stdout,"[%s] T %s size=%lld count=%d maxsize=%d minsize=%d average=%.2lf cov=%.2lf\n",cmptime,keyword,sumsize,count,maxsize,minsize,average,covl);
        sumsize=0;
        count=0;
        flag=1; 
       }
    }
  }
  if (count>0)
  {
/*
    fputs("[",stdout);
    fputs(cmptime,stdout);
    fputs("] T ",stdout);
    fputs(keyword,stdout);
    fputs(" size=",stdout);
    fprintf(stdout,"%lld",sumsize);
    fputs(" count=",stdout);
    fprintf(stdout,"%d\n",count);
*/    
    average=sumsize/count;
    covl=cov(value,count,average);
    fprintf(stdout,"[%s] T %s size=%lld count=%d maxsize=%d minsize=%d average=%.2lf cov=%.2lf\n",cmptime,keyword,sumsize,count,maxsize,minsize,average,covl);
  }
  if (*fg>1)
   {
  *fg=0;  
  }
}
void agregation(char *buf,int lines)
{
  int fg=1;
   agre(buf,lines,"WRITEDIR",&fg);
   agre(buf,lines,"READDIR",&fg);
   agre(buf,lines,"WRITE",&fg);
   agre(buf,lines,"READ",&fg);
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
