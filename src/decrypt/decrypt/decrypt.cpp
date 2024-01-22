#include <stdio.h>
#include <windows.h>

static bool DBG = 0;

#define LOG(...) do            \
{                              \
	if (DBG)                   \
		printf(__VA_ARGS__);   \
} while (0)

int main(int argc, const char* argv[])
{
	int ret = 0;
	FILE *fp_src = NULL;
	FILE *fp_dst = NULL;
	char *buf = NULL;

	if (argc < 3)
	{
		printf("usage: [exe] src_full_path dst_full_path\n");
		return 1;
	}

	if (argc > 3)
	{
		DBG = 1;
	}

	LOG("%s %s %s\n", argv[0], argv[1], argv[2]);
	// 打开文件
	fp_src = fopen(argv[1], "rb");
	fp_dst = fopen(argv[2], "wb");
	if (!fp_src || !fp_dst)
	{
		LOG("invalid param!\n");

		ret = 1;
		goto END;
	}

	// 文件大小
	fseek(fp_src, 0L, SEEK_END);
	int file_size = ftell(fp_src);
	LOG("file_size: %d\n", file_size);
	if ( file_size <= 0)
	{
		LOG("skip empty file!\n");

		ret = 1;
		goto END;
	}
	fseek(fp_src, 0L, SEEK_SET);

	buf = (char *)malloc(file_size);
	if (NULL == buf)
	{
		LOG("malloc failed[%d]!\n", file_size);
		return 1;
	}
	
	int left_size = file_size;
	while (left_size > 0)
	{
		size_t read_size = fread(buf, 1, file_size, fp_src);
		LOG("read_size: %d\n", read_size);

		if (0 == read_size)
		{
			if (feof(fp_src))
			{
				LOG("eof");// 文件末尾
			}
			else if (ferror(fp_src))
			{
				LOG("ferror[%d]", ferror(fp_src)); // 文件读取错误
			}

			break;
		}
		else
		{
			// 处理读取到的数据
			size_t write_size = fwrite(buf, 1, read_size, fp_dst);
			LOG("write_size: %d\n", write_size);

			left_size -= read_size;
			buf += read_size;
		}
	}

END:
	if (fp_src)
	{
		fclose(fp_src);
		fp_src = NULL;
	}
	if (fp_dst)
	{
		fclose(fp_dst);
		fp_dst = NULL;
	}
	if (buf)
	{
		free(buf);
		buf = NULL;
	}

	return ret;
}