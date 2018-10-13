/*
 *author: zhouqi
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>

#define _PORT 9987
#define SERVER_IP "20.0.211.6"
#define BUF_SIZE	1024

int main()
{
	/* int ip; */
	struct in_addr ip;
	inet_pton(AF_INET, SERVER_IP, &ip);

	//set server socket address
	struct sockaddr_in server_addr;
	server_addr.sin_family = AF_INET;
	server_addr.sin_addr.s_addr = ip.s_addr;
	server_addr.sin_port = htons(_PORT);

	int sd;
	if ((sd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		perror("send");
		exit(0);
	}

	if (connect(sd, (struct sockaddr*)&server_addr,
				sizeof(server_addr)) < 0) {
		perror("send");
		exit(0);
	}

	char buffer[BUF_SIZE];
	printf("input:");
		scanf("%s", buffer);
		/*
		int len = send(sd, buffer, strlen(buffer), MSG_EOR);
		*/
		int len = write(sd, buffer, strlen(buffer));
		if (len < 0) {
			perror("send");
			exit(0);
		}

	close(sd);
	return 0;
}
