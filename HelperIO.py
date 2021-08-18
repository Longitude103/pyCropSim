"""Helper methods for file I/O"""

import io
from hashlib import md5


def ReadNextWord(file, skipLines=0, delimiters=(" ", "\r", "\n")) -> str:
    """Reads the file until the next white-space and returns the read string."""
    buffer: str = ""
    while True:
        c = file.read(1)
        if not c:
            # EOF End Of File
            return buffer
        if c in delimiters:
            if len(buffer) > 0:
                if skipLines > 0:
                    SkipLines(file, skipLines)
                return buffer
        else:
            buffer += c


def ReadNextNumberSequence(file, includeText=False):
    """Reads the file until the next letter and returns and array of strings."""
    ret = []
    buffer = ""
    while True:
        c = file.read(1)
        if not c:
            # EOF End Of File
            return ret
        if c.isalpha():
            text = c + file.readline().strip()
            # print(text)
            if includeText:
                ret.append(text)
            return ret
        if c in (" ", "\r", "\n"):
            if len(buffer) > 0:
                ret.append(buffer)
                buffer = ""
        else:
            buffer += c


def ReadNextSequenceAsInteger(file, delimiters=(" ", "\r", "\n", "\t")):
    """Reads the file until the next letter and returns and array of integers."""
    ret = []
    buffer = ""
    while True:
        c = file.read(1)
        if not c:
            # EOF End Of File
            return ret
        if c.isalpha():
            file.readline()
            # print(c + file.readline().strip())
            return ret
        if c in delimiters:
            if len(buffer) > 0:
                ret.append(int(buffer))
                buffer = ""
        else:
            buffer += c


def ReadFloats(file, count):
    """Reads the specified amount of floats from the file and returns and array."""
    ret = []
    buffer = ""
    while len(ret) < count:
        c = file.read(1)
        if not c:
            # EOF End Of File
            return ret
        if c.isdigit() or c == ".":
            buffer += c
        else:
            if len(buffer) > 0:
                ret.append(float(buffer))
                buffer = ""
    return ret


def ReadNextSequenceAsFloats(file):
    """Reads the file until the next letter and returns and array of floats."""
    ret = []
    buffer = ""
    while True:
        c = file.read(1)
        if not c:
            # EOF End Of File
            return ret
        if c.isalpha():
            file.readline()
            # print(c + file.readline().strip())
            return ret
        if c in (" ", "\r", "\n"):
            if len(buffer) > 0:
                ret.append(float(buffer))
                buffer = ""
        else:
            buffer += c


def ReadIntegersInLine(file):
    """Reads the integers found in the next file line."""
    return ReadNextSequenceAsInteger(io.StringIO(file.readline()))


def ReadWholeFile(file):
    """Reads the whole file using the ReadNextNumberSequence method."""
    sof = file.tell()
    eof = file.seek(0, 2)
    print("EOF at: " + str(eof))
    file.seek(sof)
    while eof != file.tell():
        print(ReadNextNumberSequence(file))
        print("")

    print("File Read Completed")


def ReadNextFloat(file, skipLines=0) -> float:
    """Reads the file until the next invalid char and returns a float."""
    return float(ReadNextWord(file, skipLines))


def ReadNextInteger(file, skipLines=0, delimiters=(" ", "\r", "\n")) -> int:
    """Reads the file until the next invalid char and returns an integer."""
    # return int(ReadNextWord(file, skipLines, delimiters))
    buffer = ""
    while True:
        c = file.read(1)
        if not c or c.isalpha() or c in delimiters:
            if len(buffer) > 0:
                if skipLines > 0:
                    SkipLines(file, skipLines)
                return int(buffer)
        else:
            buffer += c


def ReadFloatArray(file, count, skipLines: int = 0):
    """Reads the number of floats specified and returns an array."""
    ret = []
    for _ in range(count):
        ret.append(ReadNextFloat(file))
    SkipLines(file, skipLines)
    return ret


def SplitChars(line, *lens, start: int = 0):
    """Splits the line into segments of the specified lenghts."""
    ret = []
    start = 0
    n = len(lens)
    for i in range(n):
        end = start + lens[i]
        val = line[start:end].strip()
        if val and not val.isspace():
            ret.append(val)
        start = end
    return ret


def SkipLine(file):
    """Skips one line from the file."""
    file.readline()


def SkipLines(file, count):
    """Skips the specified lines from the file."""
    temp = ""
    if count == 1:
        temp = file.readline()
    else:
        temp = file.readline(count)
    # print("Skipped: " + temp)
    return temp.strip()


def checksum(fname):
    """Returns the MD5 hash for the specified file."""
    hash_md5 = md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def compareFiles(one, other):
    """Compares the specified files with a MD5 checksum."""
    first = checksum(one)
    second = checksum(other)
    print(first)
    print(second)
    if first != second:
        print("They are different files.")
    else:
        print("They are the same file.")
