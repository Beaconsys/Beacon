#ifndef UTIL_LINUX_CLOSESTREAM_H
#define UTIL_LINUX_CLOSESTREAM_H

#include <stdio.h>
#ifdef HAVE_STDIO_EXT_H
#include <stdio_ext.h>
#endif
#include <unistd.h>

/*zhouqi#include "c.h"
#include "nls.h"*/

#ifndef HAVE___FPENDING
static inline int
__fpending(FILE *stream __attribute__((__unused__)))
{
	return 0;
}
#endif

static inline int
close_stream(FILE * stream)
{
	const int some_pending = (__fpending(stream) != 0);
	const int prev_fail = (ferror(stream) != 0);
	const int fclose_fail = (fclose(stream) != 0);
	if (prev_fail || (fclose_fail && (some_pending || errno != EBADF))) {
		if (!fclose_fail)
			errno = 0;
		return EOF;
	}
	return 0;
}

/* Meant to be used atexit(close_stdout); */
static inline void
close_stdout(void)
{
	if (close_stream(stdout) != 0 && !(errno == EPIPE)) {
		if (errno)
			warn(_("write error"));
		else
			warnx(_("write error"));
		_exit(EXIT_FAILURE);
	}

	if (close_stream(stderr) != 0)
		_exit(EXIT_FAILURE);
}

#endif /* UTIL_LINUX_CLOSESTREAM_H */
