/* sotailf.c -- tail a log file and then follow it, write to a socket.
 * Created: Tue Jan  9 15:49:21 1996 by faith@acm.org
 * Copyright 1996, 2003 Rickard E. Faith (faith@acm.org)
 * Copyright 2015 zhouqi (atmgnd@outlook.com)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 *
 * less -F and tail -f cause a disk access every five seconds.  This
 * program avoids this problem by waiting for the file size to change.
 * Hence, the file is not accessed, and the access time does not need to be
 * flushed back to disk.  This is sort of a "stealth" tail.
 */

#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <ctype.h>
#include <errno.h>
#include <getopt.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <pthread.h>
#include <poll.h>
#include <signal.h>
#ifdef HAVE_INOTIFY_INIT
#include <sys/inotify.h>
#endif
#include <err.h>

#define HAVE_USLEEP 1
#define HAVE_MEMPCPY 1

#include "nls.h"
#include "xalloc.h"
#include "strutils.h"
#include "c.h"
#include "closestream.h"
#include "aggregation.h"

#define DEFAULT_LINES  0
#define PACKAGE_STRING "tailf"
#define program_name "sotailf"

#define YANGBIN

void daemonize(const char *);

struct s_data{
	int sd; /* socket descriptor */
	char *ip; /* server ip */
	long port; /* server port */
};

pthread_t mtid;
pthread_mutex_t mpm = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t mpc = PTHREAD_COND_INITIALIZER;

/* #define _PORT 9987
#define SERVER_IP "20.0.211.6" */
#define BUF_SIZE	1024
int prepsocket(char *host, long port);
void *select_thr(void*);

static void tailf(const char *filename, int lines)
{
	char *buf, *p;
	int  head = 0;
	int  tail = 0;
	FILE *str;
	int  i;
//  fprintf(stdout,"tailf-----------------\n");
	if (!(str = fopen(filename, "r")))
		err(EXIT_FAILURE, _("cannot open %s"), filename);
	buf = xmalloc((lines ? lines : 1) * BUFSIZ);
	p = buf;
	while (fgets(p, BUFSIZ, str)) {
		if (++tail >= lines) {
			tail = 0;
			head = 1;
		}
		p = buf + (tail * BUFSIZ);
	}


	if (head) {
#ifndef YANGBIN
			fputs(buf + (i * BUFSIZ), stdout);
#else
      agregation(buf,lines);
#endif

#ifndef YANGBIN
			fputs(buf + (i * BUFSIZ), stdout);
#else
			
      agregation(buf,tail);
#endif
	} 

  else {

#ifndef YANGBIN
			fputs(buf + (i * BUFSIZ), stdout);
#else
			
      agregation(buf,tail);
#endif
	}

	fflush(stdout);
	free(buf);
	fclose(str);
}

static void
roll_file(const char *filename, off_t *size)
{
#if 0
	char buf[BUFSIZ];
	int fd;
	struct stat st;
	off_t pos;
	fd = open(filename, O_RDONLY);
	if (fd < 0)
		err(EXIT_FAILURE, _("cannot open %s"), filename);
#else
	FILE *str;
	char *buf, *p;
	struct stat st;
	int  i;
	off_t pos,output_size;
  int count=0;
	if (!(str = fopen(filename, "r")))
		err(EXIT_FAILURE, _("cannot open %s"), filename);
#endif
#if 0
	if (fstat(fd, &st) == -1)
		err(EXIT_FAILURE, _("stat failed %s"), filename);
#else
	if (stat(filename, &st) == -1)
		err(EXIT_FAILURE, _("stat failed %s"), filename);
#endif
	if (st.st_size == *size) {
  //  fprintf(stdout,"size==size\n");
    fflush(stdout);
		fclose(str);
		return;
	}
#if 0
	if (lseek(fd, *size, SEEK_SET) != (off_t)-1) {
		ssize_t rc, wc;
    char *buff,*stt,*p;
    int count;
 
    buff =malloc(100 * BUFSIZ);
    p=buff;
    count=0;
		while ((rc = read(fd, buf,sizeof(buf))) > 0) {
			wc = write(STDOUT_FILENO, buf, rc);
			if (rc != wc)
				warnx(_("incomplete write to \"%s\" (written %zd, expected %zd)\n"),
					filename, wc, rc);a
		}
		fflush(stdout);
    free(buff);
	}
#else
  pos = *size;
  output_size = st.st_size - *size;
  if (fseek(str, *size, SEEK_SET) >= 0) 
  {
    count = 0;
    if (output_size>0)
    {
      buf =(char*)malloc(1010 * BUFSIZ);
	    p = buf;
        while (fgets(p , BUFSIZ, str)) 
        {
          count++;
          if (count>=1000)
          {
            agregation(buf,count);
            count=0;
            p=buf;
          }
          // fprintf(stdout,"%s count=%d\n",p,count);
         p = buf + (count * BUFSIZ);
        }
      //fprintf(stdout,"agregation-----------count=%d\n",count);
      if (count>0) agregation(buf,count);
      count=0;
      pos=pos+output_size;
	    fflush(stdout);
      free(buf);
    }
  }
#endif
	//pos = fseek(str, 0, SEEK_CUR);
	/* If we've successfully read something, use the file position, this
	 * avoids data duplication. If we read nothing or hit an error, reset
	 * to the reported size, this handles truncated files.
	 */
  
	*size = (pos != (off_t)-1 && pos != *size) ? pos : st.st_size;

  fclose(str);
}

static void
watch_file(const char *filename, off_t *size)
{
	do 
 {  
  //fprintf(stdout,"watchfile\n");
		roll_file(filename, size);
		usleep(250000);
 // 	sleep(1);
	} while(1);
}


#ifdef HAVE_INOTIFY_INIT

#define EVENTS		(IN_MODIFY|IN_DELETE_SELF|IN_MOVE_SELF|IN_UNMOUNT)
#define NEVENTS		4

static int
watch_file_inotify(const char *filename, off_t *size)
{
	char buf[ NEVENTS * sizeof(struct inotify_event) ];
	int fd, ffd, e;
	ssize_t len;

	fd = inotify_init();
	if (fd == -1)
		return 0;

	ffd = inotify_add_watch(fd, filename, EVENTS);
	if (ffd == -1) {
		if (errno == ENOSPC)
			errx(EXIT_FAILURE, _("%s: cannot add inotify watch "
				"(limit of inotify watches was reached)."),
				filename);

		err(EXIT_FAILURE, _("%s: cannot add inotify watch."), filename);
	}

	while (ffd >= 0) {
		len = read(fd, buf, sizeof(buf));
		if (len < 0 && (errno == EINTR || errno == EAGAIN))
			continue;
		if (len < 0)
			err(EXIT_FAILURE,
				_("%s: cannot read inotify events"), filename);

		for (e = 0; e < len; ) {
			struct inotify_event *ev = (struct inotify_event *) &buf[e];

			if (ev->mask & IN_MODIFY)
				roll_file(filename, size);
			else {
				close(ffd);
				ffd = -1;
				break;
			}
			e += sizeof(struct inotify_event) + ev->len;
		}
	}
	close(fd);
	return 1;
}

#endif /* HAVE_INOTIFY_INIT */

static void __attribute__ ((__noreturn__)) usage(FILE *out)
{
	fprintf(out,
		_("Usage:\n"
		  " %s [option] -t remote_ip -p remote_port file\n"),
		program_name);
		/*program_invocation_short_name);*/

	fprintf(out, _(
		"\nOptions:\n"
		" -n, --lines NUMBER  output the last NUMBER lines\n"
		" -NUMBER             same as `-n NUMBER'\n"
		" -V, --version       output version information and exit\n"
		" -h, --help          display this help and exit\n\n"));

	exit(out == stderr ? EXIT_FAILURE : EXIT_SUCCESS);
}

/* parses -N option */
static long old_style_option(int *argc, char **argv)
{
	int i = 1, nargs = *argc;
	long lines = -1;

	while(i < nargs) {
		if (argv[i][0] == '-' && isdigit(argv[i][1])) {
			lines = strtol_or_err(argv[i] + 1,
					_("failed to parse number of lines"));
			nargs--;
			if (nargs - i)
				memmove(argv + i, argv + i + 1,
						sizeof(char *) * (nargs - i));
		} else
			i++;
	}
	*argc = nargs;
	return lines;
}

void wait_connect(int i){
	pthread_mutex_lock(&mpm);
	pthread_cond_wait(&mpc, &mpm);
	pthread_mutex_unlock(&mpm);
}

int main(int argc, char **argv)
{
	const char *filename;
	long lines ;
	int ch;
	struct stat st;
	off_t size = 0;
	pthread_t tid;
	struct s_data sdata={0, 0, 0};
	if(signal(SIGPIPE, SIG_IGN) == SIG_ERR)
	       errx(5, "%s:%d: signal SIGPIPE binding fails.\n", __FILE__, __LINE__);
	if(signal(SIGUSR1, wait_connect) == SIG_ERR)
	       errx(5, "%s:%d: signal SIGUSR1 binding fails.\n", __FILE__, __LINE__);

	static const struct option longopts[] = {
		{ "lines",   required_argument, 0, 'n' },
		{ "host",    required_argument,0, 't' }, /* the server ip, ping it */
		{ "port",    required_argument,0, 'p' }, /* the tcp port, above 1024 */
		{ "version", no_argument,	0, 'V' },
		{ "help",    no_argument,	0, 'h' },
		{ NULL,      0, 0, 0 }
	};

	setlocale(LC_ALL, "");
	/* zhouqi bindtextdomain(PACKAGE, LOCALEDIR);
	textdomain(PACKAGE);*/
  
//	atexit(close_stdout);

	/* zhouqi begin */
	/*
	daemonize(_(argv[0]));
	*/
	daemonize(_(argv[0]));
  
	lines = old_style_option(&argc, argv);
	if (lines < 0)
		lines = DEFAULT_LINES;

	while ((ch = getopt_long(argc, argv, "t:p:n:N:Vh", longopts, NULL)) != -1)
		switch((char)ch) {
		case 'n':
		case 'N':
			lines = strtol_or_err(optarg,
					_("failed to parse number of lines"));
			break;
		case 't':
			sdata.ip = strndup(optarg, 16);
			if(sdata.ip == 0){
				errx(34, "failed to parse host ip.");
			}
			break;
		case 'p':
			sdata.port = strtol_or_err(optarg,
					_("failed to parse number of port"));
			break;
		case 'V':
			printf(_("%s from %s\n"), program_name,
						  PACKAGE_STRING);
			exit(EXIT_SUCCESS);
		case 'h':
			usage(stdout);
		default:
			usage(stderr);
		}
/*	fprintf(stderr, "host: %s\nport: %lu\n", sdata.ip, sdata.port);
	exit(45); 
*/
	if(sdata.ip == 0 || sdata.port == 0)
		usage(stderr);
	
	sdata.sd = prepsocket(sdata.ip, sdata.port);
	/*if(sdata.sd == -1){
		fprintf(stderr, "connect to ..., first trying fiald, exi..\n");
		exit(9);
	}*/
	

	while((sdata.sd = prepsocket(sdata.ip, sdata.port)) == -1){
		fprintf(stderr, "connect to ..., first trying fiald, try again\n");
		//usleep(3 * 1000 * 1000);
    sleep(1);
	}
	fprintf(stderr, "connect to succ...\n");

	if( dup2(sdata.sd, 1) == -1){
		errx(3, "dup2 failed %d", __LINE__);
	}else{
		/* when we dup a socket, do not close the old one. by zhouqi */
		/* close(sd); */
	}
	mtid = pthread_self();
	if(pthread_create(&tid, NULL, select_thr, &sdata) != 0){
		errx(99, "pthread create failed %d", __LINE__);
	}

	/* zhouqi end */

	if (argc == optind)
		errx(EXIT_FAILURE, _("no input file specified"));

	filename = argv[optind];
	if (stat(filename, &st) != 0)
		err(EXIT_FAILURE, _("stat failed %s"), filename);

	size = st.st_size;
  tailf(filename, lines);
#ifdef HAVE_INOTIFY_INIT
	if (!watch_file_inotify(filename, &size))
#endif
		watch_file(filename, &size);

	return EXIT_SUCCESS;
}

int prepsocket(char *host, long port){
	/* int ip; */
	struct in_addr ip;
	inet_pton(AF_INET, host, &ip);

	//set server socket address
	struct sockaddr_in server_addr;
	server_addr.sin_family = AF_INET;
	server_addr.sin_addr.s_addr = ip.s_addr;
	server_addr.sin_port = htons(port);

	int sd;
	if ((sd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		warnx("socket failed.");
		return -1;
	}

	if (connect(sd, (struct sockaddr*)&server_addr,
				sizeof(server_addr)) < 0) {
		warnx("connect failed.");
		return -1;
	}

	return sd;

	return -1;
}

void *select_thr(void *sdptr){
	/* forget select, by zhouqi
	fd_set fset;

	FD_ZERO(&fset);
	FD_SET(*sdptr, &fset);
	*/

	int sd;
	struct pollfd pfs[1];
	pfs[0].fd = ((struct s_data *)sdptr)->sd;
	pfs[0].events = POLLERR | POLLHUP | POLLNVAL;

	/* we should define _GUN_SOURCE, so we can use ROLLRDHUP */
	pfs[0].events = POLLERR | POLLHUP | POLLNVAL | POLLRDHUP;

	for(;;){
		if(poll(pfs, 1, -1) <= 0){
			errx(987, "poll error %d", __LINE__);
		}

		pthread_kill(mtid, SIGUSR1);

		for(sd = prepsocket(((struct s_data *)sdptr)->ip,((struct s_data *)sdptr)->port ); \
			sd == -1; \
			sd = prepsocket(((struct s_data *)sdptr)->ip, ((struct s_data *)sdptr)->port)){
			fprintf(stderr, "prep in thr\n");
			sleep(1);
		}
		//sd = prepsocket();

		if(((struct s_data *)sdptr)->sd != sd)
			close(*(int *)sdptr);

		((struct s_data *)sdptr)->sd = sd;
		pfs[0].fd = sd;
		if( dup2(sd, 1) == -1){
			errx(30, "dup2 in thr fails %d", __LINE__);
		}
		
		pthread_cond_signal(&mpc);

		fprintf(stderr, "select_thr ocuured\n");
	}

	return 0;
}
