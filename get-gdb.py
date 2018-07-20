#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re, shutil, multiprocessing

GDB_VERSION_LIST = ("6.1.1", "6.2.1", "6.3", "6.4", "6.5", "6.6",
                    "6.7", "6.7.1", "6.8", "7.0.1", "7.1", "7.2", "7.3.1",
                    "7.4.1", "7.5.1", "7.6.2", "7.7.1", "7.8", "7.8.1",
                    "7.8.2", "7.9", "7.9.1", "7.10", "7.10.1", "7.11", "7.11.1",
                    "7.12", "7.12.1", "8.0", "8.0.1", "8.1")
GDB_VERSION_HAVE_A = "7.2"
GDB_VERSION_HAVE_XZ = "7.8"

GET_GDB_URL = "https://raw.githubusercontent.com/teawater/get-gdb/master/"
PATCH_6_8 = "handle-siginfo-6_8.patch"
PATCH_7_0 = "handle-siginfo-7_0.patch"
PATCH_7_1_TO_7_2 = "handle-siginfo-7_1-to-7_2.patch"
PATCH_7_3_TO_7_4 = "handle-siginfo-7_3-to-7_4.patch"
PATCH_7_8_2_ZONE = "handle-kernel-zone-7_8_2.patch"

DOWNLOAD_TOOL = "axel"

class Lang(object):
    '''Language class.'''
    def __init__(self, language="en"):
        self.data = {}
        self.language = language
        self.is_set = False
        self.add('Call command "%s" failed. ',
                 '调用命令"%s"失败。 ')
        self.add('Please install "%s" before go to next step.',
                 '在进行下一步以前请先安装软件包"%s"。')
        self.add('Input "y" and press "Enter" to continue',
                 '输入"y"后按回车键继续')
        self.add("Install packages failed.",
                 "安装包失败。")
        self.add('"%s" is not right.',
                 '"%s"不正确。')
        self.add('Current system is "%s".',
                 '当前系统是"%s".')
        self.add("Current system is not complete support.  Need execute some commands with yourself.\nIf you want KGTP support your system, please report to https://github.com/teawater/get-gdb/issues or teawater@gmail.com.",
                 "当前系统还没有被支持，需要手动执行一些命令。\n如果你希望KGTP支持你的系统，请汇报这个到 https://github.com/teawater/get-gdb/issues 或者 teawater@gmail.com。")
        self.add("Which version of GDB do you want to install?",
                 "你要安装哪个版本的GDB?")
        self.add("Build from source *without* check GDB in current system?",
                 "*不*检查当前系统，直接从源码编译GDB？")
        self.add('GDB in "%s" is OK for use.',
                 '在"%s"中的GDB可用。')
        self.add('GDB in software source is older than "%s".',
                 '软件源中的GDB比"%s"老。')
        self.add("Build and install GDB ...",
                 "编译和安装GDB...")
        self.add("Do you want to install GDB after it is built?",
                 "需要在编译GDB后安装它吗？")
        self.add("Please input the PREFIX directory that you want to install(GDB will be installed to PREFIX/bin/):",
                 "请输入安装的PREFIX目录（GDB将被安装在 PREFIX/bin/ 目录中）：")
        self.add("Please input the directory that you want to build GDB:",
                 '请输入编译GDB的目录：')
        self.add("Download GDB source package failed.",
                 '下载GDB源码包失败。')
        self.add("Uncompress GDB source package failed.",
                 '解压缩GDB源码包失败。')
        self.add("Config GDB failed.",
                 "配置GDB失败。")
        self.add("Build GDB failed.",
                 "编译GDB失败。")
        self.add("Install GDB failed.",
                 "安装GDB失败。")
        self.add('GDB %s is available in "%s".',
                 'GDB %s在"%s"。')
        self.add('"%s" exist.  Use it without download a new one?',
                 '"%s"存在，是否不下载而直接使用其？')
        self.add("Cannot get version of GDB in software source, build from source code?",
                 "不能取得软件源中GDB的版本，从源码编译？")
        self.add('Please input the number of jobs to compile GDB:[%d]',
                 '请输入编译GDB的任务数量:[%d]')
        self.add("Current architecture",
                 "当前系统体系结构")
        self.add("Input other",
                 "输入其他体系结构")
        self.add("Which architecture do you want to build?",
                 "你要编译哪个体系结构？")
        self.add("Input the architecture:",
                 "输入体系结构:")
        self.add("Got code issue.\nPlease report to https://github.com/teawater/get-gdb/issues or teawater@gmail.com.",
                 "代码有错。\n请汇报这个到 https://github.com/teawater/get-gdb/issues 或者 teawater@gmail.com。")

    def set_language(self, language):
        if language != "":
            if language[0] == "c" or language[0] == "C":
                self.language = "cn"
            else:
                self.language = "en"
            self.is_set = True

    def add(self, en, cn):
        self.data[en] = cn

    def string(self, s):
        if self.language == "en" or (not self.data.has_key(s)):
            return s
        return self.data[s]

def select_from_list(entry_list, default_entry, introduction, return_number=False):
    if type(entry_list) == dict:
        entry_dict = entry_list
        entry_list = list(entry_dict.keys())
        entry_is_dict = True
    else:
        entry_is_dict = False
    while True:
        default = -1
        default_str = ""
        for i in range(0, len(entry_list)):
            if entry_is_dict:
                print("[%d] %s %s" %(i, entry_list[i], entry_dict[entry_list[i]]))
            else:
                print("[%d] %s" %(i, entry_list[i]))
            if default_entry != "" and entry_list[i] == default_entry:
                default = i
                default_str = "[%d]" %i
        try:
            select = input(introduction + default_str)
        except SyntaxError:
            select = default
        except Exception:
            select = -1
        if select >= 0 and select < len(entry_list):
            break

    if return_number:
        return select

    return entry_list[select]

def yes_no(string="", has_default=False, default_answer=True):
    if has_default:
        if default_answer:
            default_str = " [Yes]/No:"
        else:
            default_str = " Yes/[No]:"
    else:
        default_str = " Yes/No:"
    while True:
        s = raw_input(string + default_str)
        if len(s) == 0:
            if has_default:
                return default_answer
            continue
        if s[0] == "n" or s[0] == "N":
            return False
        if s[0] == "y" or s[0] == "Y":
            return True

def get_distro():
    if os.path.exists("/etc/redhat-release"):
        return "Redhat"

    try:
        fp = open("/etc/issue", "r")
        version = fp.readline().lower()
        fp.close()
        if re.match('.*ubuntu.*', version):
            return "Ubuntu"
        elif re.match('.*opensuse.*', version):
            return "openSUSE"
    except:
        pass

    return "Other"

def get_cmd(cmd, first=True):
    f = os.popen(cmd)
    if first:
        v = f.readline().rstrip()
    else:
        v = f.readlines()
    f.close()
    return v

def retry(string="", ret=-1):
    ignore = False
    while True:
        s = raw_input(string + lang.string(" [Retry]/Ignore/Exit:"))
        if len(s) == 0 or s[0] == 'r' or s[0] == 'R':
            break
        if s[0] == 'I' or s[0] == 'i':
            ignore = True
            break
        if s[0] == "E" or s[0] == "e":
            exit(ret)
    return ignore

def call_cmd(cmd, fail_str="", chdir="", outside_retry=False):
    '''
    Return True if call cmd success.
    '''
    if fail_str == "":
        fail_str = lang.string('Call command "%s" failed. ') %cmd
    if chdir != "":
        os.chdir(chdir)
    while True:
        ret = os.system(cmd)
        if ret == 0 or retry(fail_str, ret):
            break
        if outside_retry:
            return False

    return True

def version_get(s):
    ret = re.match(r'^GNU gdb (.+) (\d+\.\d+.\d+).*$', s)
    if not ret:
        ret = re.match(r'^GNU gdb (.+) (\d+\.\d+).*$', s)
        if not ret:
            return -1

    return str(ret.group(2))

def get_gdb_version(gdb):
    try:
        v = get_cmd(gdb + " -v")
    except:
        return -1

    return version_get(v)

def get_source_version(distro, name):
    if distro == "Redhat":
        try:
            v = get_cmd("yum list " + name, False)
        except:
            return 0
        if len(v) <= 0:
            return 0
        v = v[-1]
        if not re.match('^'+name, v):
            return 0
    elif distro == "Ubuntu":
        v = get_cmd("apt-cache showpkg " + name, False)
        for i in range(0, len(v)):
            if v[i].strip() == "Versions:":
                break
            pass
        else:
            return 0
        v = v[i + 1]
    elif distro == "openSUSE":
        try:
            v = get_cmd("zypper info " + name, False)
        except:
            return 0
        got_name = False
        got_version = False
        for line in v:
            if got_name and re.match('^Version: ', line):
                got_version = True
                v = line
                break
            if re.match('^Name: '+name, line):
                got_name = True
    else:
        return 0

    return version_get(v)

def install_packages(distro, packages, auto=False):
    #Remove the package that doesn't need install from packages
    if os.geteuid() != 0:
        sudo = "sudo "
    else:
        sudo = ""
    if distro != "Other":
        tmp_packages = []
        for i in range(0, len(packages)):
            ret = 1
            if distro == "Redhat" or distro == "openSUSE":
                ret = os.system("rpm -q " + packages[i])
            elif distro == "Ubuntu":
                ret = os.system("dpkg -s " + packages[i])
            if ret != 0:
                tmp_packages.append(packages[i])
        packages = tmp_packages
    if len(packages) == 0:
        return

    packages = " ".join(packages)
    while True:
        ret = 0
        if distro == "Redhat":
            ret = os.system(sudo + "yum -y install " + packages)
        elif distro == "Ubuntu":
            ret = os.system(sudo + "apt-get -y --force-yes install " + packages)
        elif distro == "openSUSE":
            ret = os.system(sudo + "zypper -n install --oldpackage " + packages)
        else:
            if auto:
                return
            while True:
                print(lang.string('Please install \"%s\" before go to next step.') %packages)
                s = raw_input(lang.string('Input "y" and press "Enter" to continue'))
                if len(s) > 0 and (s[0] == 'y' or s[0] == "Y"):
                    return

        if ret == 0 or retry(lang.string("Install packages failed."), ret):
            break

def input_dir(msg, default=""):
    if default != "":
        default_str = '[' + default + ']'
    else:
        default_str = ''
    while True:
        ret_dir = raw_input(msg + default_str)
        if ret_dir == "":
            ret_dir = default
        if ret_dir == "":
            continue
        if not os.path.isdir(ret_dir):
            print(lang.string('"%s" is not right.') %ret_dir)
            continue
        return os.path.realpath(ret_dir)

def patch_dir(patch_name):
    global build_dir, install_version

    try:
        os.remove(patch_name)
    except:
        pass
    if not call_cmd("wget " + GET_GDB_URL + patch_name, "", build_dir + "/gdb-" + install_version + "/", True):
        return False
    if not call_cmd("patch -p1 < " + patch_name, "", build_dir + "/gdb-" + install_version + "/", True):
        return False

    return True

def version_compare(a, b, same_return_true = False):
    def version_array(v):
        va = v.split('.')
        if len(va) == 2:
            va.append(0)
        if len(va) != 3:
            print "Error version: ", v, "\n", lang.string("Got code issue.\nPlease report to https://github.com/teawater/get-gdb/issues or teawater@gmail.com.")
            exit(1)
        for i in range(3):
            va[i] = int(va[i])
        return va
    a = version_array(a)
    b = version_array(b)
    for i in range(3):
        if a[i] > b[i]:
            return True
        elif a[i] < b[i]:
            return False
        elif i == 2 and same_return_true:
            return True
    return False

lang = Lang()
lang.set_language(select_from_list(("English", "Chinese"), "", "Which language do you want to use?"))

distro = get_distro()
if distro != "Other":
    print(lang.string('Current system is "%s".') %distro)
else:
    print(lang.string("Current system is not complete support.  Need execute some commands with yourself.\nIf you want KGTP support your system, please report to https://github.com/teawater/get-gdb/issues or teawater@gmail.com."))

install_version = select_from_list(GDB_VERSION_LIST, GDB_VERSION_LIST[len(GDB_VERSION_LIST)-1], lang.string("Which version of GDB do you want to install?"))

if version_compare(install_version, GDB_VERSION_HAVE_XZ, True):
    gdb_name = "gdb-" + install_version + ".tar.xz"
elif version_compare(install_version, GDB_VERSION_HAVE_A):
    gdb_name = "gdb-" + install_version + ".tar.bz2"
else:
    gdb_name = "gdb-" + install_version + "a.tar.bz2"

#Target
target_list = (lang.string("Current architecture"), lang.string("Input other"),
               "x86_64-linux", "arm-linux", "aarch64-linux", "mips-linux")
num = select_from_list(target_list,
                       lang.string("Current architecture"),
                       lang.string("Which architecture do you want to build?"), True)
target_cmd = "--target="
arch = ""
if num == 0:
    target_cmd = ""
elif num >= 2:
    target_cmd += target_list[num]
    arch = target_list[num]
elif num == 1:
    while True:
        s = raw_input(lang.string("Input the architecture:"))
        if len(s) != 0:
            break
    target_cmd += s
    arch = s

if arch != "":
    arch += "-"

if target_cmd == "" and not yes_no(lang.string("Build from source *without* check GDB in current system?")):
    if distro == "Other":
        install_packages(distro, ["gdb"])

    while True:
        #Find GDB from PATH
        for p in os.environ.get("PATH").split(':'):
            if os.path.isfile(p + "/gdb") and version_compare(get_gdb_version(p + "/gdb"), install_version, True):
                print(lang.string('GDB in "%s" is OK for use.') %(p + "/gdb"))
                exit(0)

        #Try to install GDB from software source
        if distro != "Other":
            print(lang.string("Check the software source..."))
            version = get_source_version(distro, "gdb")
            if version == -1 and yes_no(lang.string("Cannot get version of GDB in software source, build from source code?")):
                break
            if version_compare(version, install_version, True):
                install_packages(distro, ["gdb"])
            else:
                print(lang.string('GDB in software source is older than "%s".') %install_version)
                break

#Install GDB from source code
print lang.string("Build and install GDB ...")
if yes_no(lang.string("Do you want to install GDB after it is built?")):
    install_dir = input_dir(lang.string("Please input the PREFIX directory that you want to install(GDB will be installed to PREFIX/bin/):"), "/usr/local/")
else:
    install_dir = ""

build_dir = input_dir(lang.string("Please input the directory that you want to build GDB:"), os.getcwd())
os.chdir(build_dir)

compile_job_number = multiprocessing.cpu_count()
while True:
    s = raw_input(lang.string('Please input the number of jobs to compile GDB:[%d]') %compile_job_number)
    if len(s) == 0:
        break
    try:
        compile_job_number = int(s)
    except:
        continue
    break
compile_cmd = "make -j " + str(compile_job_number) + " all"

if distro == "Ubuntu":
    install_packages(distro, ["gcc", "texinfo", "m4", "flex", "bison",
                              "libncurses5-dev", "libexpat1-dev",
                              "python-dev", "axel", "wget", "xz"])
elif distro == "openSUSE":
    install_packages(distro, ["gcc", "texinfo", "m4", "flex",
                              "bison","ncurses-devel", "libexpat-devel",
                              "python-devel", "axel","make", "wget", "xz"])
else:
    install_packages(distro, ["gcc", "gcc-c++", "texinfo", "m4", "flex",
                              "bison","ncurses-devel", "expat-devel",
                              "python-devel", "axel", "wget", "xz"])

if not os.path.exists("/usr/bin/axel"):
    DOWNLOAD_TOOL = "wget"

while True:
    if (not os.path.isfile(build_dir + "/" + gdb_name) 
        or not yes_no(lang.string('"%s" exist.  Use it without download a new one?') %(build_dir + "/" + gdb_name))):
        try:
            os.remove(build_dir + "/" + gdb_name)
        except:
            pass
        if not call_cmd(DOWNLOAD_TOOL + " http://ftp.gnu.org/gnu/gdb/" + gdb_name, lang.string("Download GDB source package failed."), "", True):
            continue
    shutil.rmtree(build_dir + "/gdb-" + install_version + "/", True)
    if not call_cmd("tar vxf " + gdb_name + " -C ./", lang.string("Uncompress GDB source package failed."), "", True):
        continue
    #shutil.rmtree(build_dir + "/gdb-" + install_version + "/", True)
    if install_dir == "":
        config_cmd = "./configure " + target_cmd + " --disable-sid --disable-rda --disable-gdbtk --disable-tk --disable-itcl --disable-tcl --disable-libgui --disable-ld --disable-gas --disable-binutils --disable-gprof --with-gdb-datadir=" + build_dir + "/gdb-" + install_version + "/" + "/gdb/data-directory/ --enable-build-warnings=no"
    else:
        config_cmd = "./configure " + target_cmd + " --prefix=" + install_dir +" --disable-sid --disable-rda --disable-gdbtk --disable-tk --disable-itcl --disable-tcl --disable-libgui --disable-ld --disable-gas --disable-binutils --disable-gprof --enable-build-warnings=no"
    if not call_cmd(config_cmd, lang.string("Config GDB failed."), build_dir + "/gdb-" + install_version + "/", True):
        continue

    if install_version == "7.8.2":
        if not patch_dir(PATCH_7_8_2_ZONE):
                continue

    if (version_compare(install_version, "6.8", True) and version_compare("7.4", install_version, True)) or install_version == "7.8.2":
        if os.system(compile_cmd) != 0:
            if install_version == "6.8":
                patch_name = PATCH_6_8
            elif install_version == "7.0":
                patch_name = PATCH_7_0
            elif version_compare(install_version, "7.1", True) and version_compare("7.2", install_version, True):
                patch_name = PATCH_7_1_TO_7_2
            elif version_compare(install_version, "7.3", True) and version_compare("7.4", install_version, True):
                patch_name = PATCH_7_3_TO_7_4
            shutil.rmtree(build_dir + "gdb-" + install_version + "/" + patch_name, True)
            if not patch_dir(patch_name):
                continue
            #if not call_cmd("axel " + GET_GDB_URL + patch_name, "", build_dir + "/gdb-" + install_version + "/", True):
                #continue
            #if not call_cmd("patch -p1 < " + patch_name, "", build_dir + "/gdb-" + install_version + "/", True):
                #continue
            if not call_cmd(compile_cmd, lang.string("Build GDB failed."), build_dir + "/gdb-" + install_version + "/", True):
                continue
    else:
        if not call_cmd(compile_cmd, lang.string("Build GDB failed."), build_dir + "/gdb-" + install_version + "/", True):
            continue
    if install_dir:
        if not os.access(install_dir, os.W_OK):
            sudo_cmd = "sudo "
        else:
            sudo_cmd = ""
        if not call_cmd(sudo_cmd + "make install", lang.string("Install GDB failed."),build_dir + "/gdb-" + install_version + "/", True):
            continue
        print(lang.string('GDB %s is available in "%s".') %(install_version, install_dir + "/bin/" + arch + "gdb"))
    else:
        print(lang.string('GDB %s is available in "%s".') %(install_version, build_dir + "/gdb-" + install_version + "/gdb/gdb"))
    break
