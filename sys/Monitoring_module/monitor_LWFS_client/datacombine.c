#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<sys/types.h>
#include<sys/stat.h>
#include<fcntl.h>
#include"datacombine.h"
void computew(char*st,char*strtime,int *size,char*stroffset)
{
  char *strtmp,*strtmp1;
  char strsize[15];
  int j;
  strncpy(strtime,st+1,19);
  strtime[19]='\0';
  if (strstr(strstr(st,"WRITE"),"size"))
  {
    strtmp=strstr(strstr(st,"WRITE"),"size");
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

void computer(char*st,char*strtime,int *size,char*stroffset)
{
  char *strtmp,*strtmp1;
  char strsize[15];
  int j;
  strncpy(strtime,st+1,19);
  strtime[19]='\0';
  if (strstr(strstr(st,"READ"),"size"))
  {
    strtmp=strstr(strstr(st,"READ"),"size");
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

void combine(char *st,char *buf,int *iter)
{
  char *p,*pst;
  char strtime[20];
  char cmptime[20];
  char stroffset[30];
  char cmpoffset[30];
  int size;
  long long sumsize;
  int i=*iter;
  if(!strchr(st,'['))
    return;
  if (!((strstr(st,"OPEN"))||(strstr(st,"WRITE"))||(strstr(st,"READ")))) 
    return;
  if(strstr(st,"OPEN")||(strstr(st,"OPENDIR")))
  {
    fputs(st,stdout);
    return;
  }
   if ((strstr(st,"WRITEDIR"))&&(strstr(strstr(st,"WRITEDIR"),"size"))) 
  { 
    computew(st,strtime,&size,stroffset);
    sumsize=size;
    strcpy(cmptime,strtime);
    strcpy(cmpoffset,stroffset);

    i++;
    st=buf+(i*BUFSIZ);
    if ((strstr(st,"WRITEDIR"))&&(strstr(strstr(st,"WRITEDIR"),"=>")))
    {
      i++;
      pst=buf+(i*BUFSIZ);
      if (strstr(pst,"GETXATTR")) i+=2;
    }
    st=buf+(i*BUFSIZ);  
    while ((strstr(st,"WRITEDIR"))&&(strstr(strstr(st,"WRITEDIR"),"size")))
    {
      computew(st,strtime,&size,stroffset);
      i++;
      st=buf+(i*BUFSIZ);
      if ((strstr(st,"WRITEDIR"))&&(strstr(strstr(st,"WRITEDIR"),"=>")))
      {
        i++;
        pst=buf+(i*BUFSIZ);
        if (strstr(pst,"GETXATTR")) i+=2;
      }

      if (!strcmp(strtime,cmptime)) 
      {
        sumsize+=size;
        strcpy(cmpoffset,stroffset);
        st=buf+(i*BUFSIZ);
      }
      else 
      {
        fputs("[",stdout);
        fputs(cmptime,stdout);
        fputs("] T ",stdout);
        fputs(" WRITEDIR",stdout);
        fputs(" size=",stdout);
        fprintf(stdout,"%lld",sumsize);
        fputs(" offset=",stdout);
        fputs(cmpoffset,stdout); 
        fputs("\n",stdout);
        sumsize=size;
        strcpy(cmptime,strtime);
        strcpy(cmpoffset,stroffset);
        st=buf+(i*BUFSIZ);   

      }

    }
    fputs("[",stdout);
    fputs(cmptime,stdout);
    fputs("] T ",stdout);
    fputs(" WRITEDIR",stdout);
    fputs(" size=",stdout);
    fprintf(stdout,"%lld",sumsize);
    fputs(" offset=",stdout);
    fputs(cmpoffset,stdout); 
    fputs("\n",stdout);

  } 
  if ((strstr(st,"READDIR"))&&(strstr(strstr(st,"READDIR"),"size"))) 
  { 
    computer(st,strtime,&size,stroffset);
    sumsize=size;
    strcpy(cmptime,strtime);
    strcpy(cmpoffset,stroffset);

    i++;
    st=buf+(i*BUFSIZ);
    if ((strstr(st,"READDIR"))&&(strstr(strstr(st,"READDIR"),"=>")))
    {
      i++;
      pst=buf+(i*BUFSIZ);
      if (strstr(pst,"GETXATTR")) i+=2;
    }
    st=buf+(i*BUFSIZ);  
    while ((strstr(st,"READDIR"))&&(strstr(strstr(st,"READDIR"),"size")))
    {
      computer(st,strtime,&size,stroffset);
      i++;
      st=buf+(i*BUFSIZ);
      if ((strstr(st,"READDIR"))&&(strstr(strstr(st,"READDIR"),"=>")))
      {
        i++;
        pst=buf+(i*BUFSIZ);
        if (strstr(pst,"GETXATTR")) i+=2;
      }

      if (!strcmp(strtime,cmptime)) 
      {
        sumsize+=size;
        strcpy(cmpoffset,stroffset);
        st=buf+(i*BUFSIZ);
      }
      else 
      {
        fputs("[",stdout);
        fputs(cmptime,stdout);
        fputs("] T ",stdout);
        fputs(" READDIR",stdout);
        fputs(" size=",stdout);
        fprintf(stdout,"%lld",sumsize);
        fputs(" offset=",stdout);
        fputs(cmpoffset,stdout); 
        fputs("\n",stdout);
        sumsize=size;
        strcpy(cmptime,strtime);
        strcpy(cmpoffset,stroffset);
        st=buf+(i*BUFSIZ);   

      }

    }
    fputs("[",stdout);
    fputs(cmptime,stdout);
    fputs("] T ",stdout);
    fputs(" READDIR",stdout);
    fputs(" size=",stdout);
    fprintf(stdout,"%lld",sumsize);
    fputs(" offset=",stdout);
    fputs(cmpoffset,stdout); 
    fputs("\n",stdout);

  }

  if ((strstr(st,"WRITE"))&&(strstr(strstr(st,"WRITE"),"size"))&&(!strstr(st,"WRITEDIR"))) 
  { 
    computew(st,strtime,&size,stroffset);
    sumsize=size;
    strcpy(cmptime,strtime);
    strcpy(cmpoffset,stroffset);

    i++;
    st=buf+(i*BUFSIZ);
    if ((strstr(st,"WRITE"))&&(strstr(strstr(st,"WRITE"),"=>")))
    {
      i++;
      pst=buf+(i*BUFSIZ);
      if (strstr(pst,"GETXATTR")) i+=2;
    }
    st=buf+(i*BUFSIZ);  
    while ((strstr(st,"WRITE"))&&(strstr(strstr(st,"WRITE"),"size")))
    {
      computew(st,strtime,&size,stroffset);
      i++;
      st=buf+(i*BUFSIZ);
      if ((strstr(st,"WRITE"))&&(strstr(strstr(st,"WRITE"),"=>")))
      {
        i++;
        pst=buf+(i*BUFSIZ);
        if (strstr(pst,"GETXATTR")) i+=2;
      }

      if (!strcmp(strtime,cmptime)) 
      {
        sumsize+=size;
        strcpy(cmpoffset,stroffset);
        st=buf+(i*BUFSIZ);
      }
      else 
      {
        fputs("[",stdout);
        fputs(cmptime,stdout);
        fputs("] T ",stdout);
        fputs(" WRITE",stdout);
        fputs(" size=",stdout);
        fprintf(stdout,"%lld",sumsize);
        fputs(" offset=",stdout);
        fputs(cmpoffset,stdout); 
        fputs("\n",stdout);
        sumsize=size;
        strcpy(cmptime,strtime);
        strcpy(cmpoffset,stroffset);
        st=buf+(i*BUFSIZ);   

      }

    }
    fputs("[",stdout);
    fputs(cmptime,stdout);
    fputs("] T ",stdout);
    fputs(" WRITE",stdout);
    fputs(" size=",stdout);
    fprintf(stdout,"%lld",sumsize);
    fputs(" offset=",stdout);
    fputs(cmpoffset,stdout); 
    fputs("\n",stdout);


  }

  if ((strstr(st,"READ"))&&(strstr(strstr(st,"READ"),"size"))&&(!strstr(st,"READDIR"))) 
  { 
    computer(st,strtime,&size,stroffset);
    sumsize=size;
    strcpy(cmptime,strtime);
    strcpy(cmpoffset,stroffset);

    i++;
    st=buf+(i*BUFSIZ);
    if ((strstr(st,"READ"))&&(strstr(strstr(st,"READ"),"=>")))
    {
      i++;
      pst=buf+(i*BUFSIZ);
      if (strstr(pst,"GETXATTR")) i+=2;
    }
    st=buf+(i*BUFSIZ);  
    while ((strstr(st,"READ"))&&(strstr(strstr(st,"READ"),"size")))
    {
      computer(st,strtime,&size,stroffset);
      i++;
      st=buf+(i*BUFSIZ);
      if ((strstr(st,"READ"))&&(strstr(strstr(st,"READ"),"=>")))
      {
        i++;
        pst=buf+(i*BUFSIZ);
        if (strstr(pst,"GETXATTR")) i+=2;
      }

      if (!strcmp(strtime,cmptime)) 
      {
        sumsize+=size;
        strcpy(cmpoffset,stroffset);
        st=buf+(i*BUFSIZ);
      }
      else 
      {
        fputs("[",stdout);
        fputs(cmptime,stdout);
        fputs("] T ",stdout);
        fputs(" READ",stdout);
        fputs(" size=",stdout);
        fprintf(stdout,"%lld",sumsize);
        fputs(" offset=",stdout);
        fputs(cmpoffset,stdout); 
        fputs("\n",stdout);
        sumsize=size;
        strcpy(cmptime,strtime);
        strcpy(cmpoffset,stroffset);
        st=buf+(i*BUFSIZ);   

      }

    }
    fputs("[",stdout);
    fputs(cmptime,stdout);
    fputs("] T ",stdout);
    fputs(" READ",stdout);
    fputs(" size=",stdout);
    fprintf(stdout,"%lld",sumsize);
    fputs(" offset=",stdout);
    fputs(cmpoffset,stdout); 
    fputs("\n",stdout);


  }
*iter=i;
}
#ifdef DC
int main()
{
  char*filename;
  int lines;
  char *buf,*p,*st;
  int head=0;
  int tail=0;
  FILE *str;
  int i;
  filename="/root/genzong";
  lines=4000;
  str=fopen(filename,"r");
  buf=(char*)malloc((lines ? lines :1)*BUFSIZ);
  p=buf;
  while(fgets(p,BUFSIZ,str))
  {
    if (++tail >=lines)
    {
      tail=0;
      head=1;
    }
    p=buf+(tail*BUFSIZ);
  }
  printf("tail=%d head=%d\n",tail,head);
  if (head)
  {
    for (i=tail;i<lines;i++)
    {
      st=buf+(i*BUFSIZ);
      combine(st,buf,&i);
    }
    for (i = 0; i < tail; i++)
    {
      st=buf+(i*BUFSIZ);
      combine(st,buf,&i);
    }
  } 
  else {
    for (i = head; i < tail; i++)
    {
      st=buf+(i*BUFSIZ);
      combine(st,buf,&i);

    }
  }
  fflush(stdout);
  free(buf);
  fclose(str);
  return 0;

}
#endif
