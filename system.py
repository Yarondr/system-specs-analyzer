from tkinter import *
import cpuinfo
import GPUtil
import psutil
import platform
from threading import Thread


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def render_title(title):
    return "="*40 + f" {title} " + "="*40

def render_subtitle(title):
    return "-"*38 + f" {title} " + "-"*38

# System Information
def get_base_system_info():
    uname = platform.uname()
    return "\n" + render_title("System Information") + "\n\n" + \
        f"System: {uname.system}" + "\n" + \
        f"PC Name: {uname.node}" + "\n" + \
        f"Release: {uname.release}" + "\n" + \
        f"Version: {uname.version}" + "\n" + \
        f"Machine: {uname.machine}" + "\n" + \
        f"Processor: {uname.processor}" + "\n\n"


# CPU information
def get_cpu_info():
    cpufreq = psutil.cpu_freq()

    return render_title("CPU Info") + "\n\n" + \
        f"Brand Name: {cpuinfo.get_cpu_info()['brand_raw']}" + "\n" + \
        f"Physical cores: {psutil.cpu_count(logical=False)}" + "\n" + \
        f"Total cores: {psutil.cpu_count(logical=True)}" + "\n" + \
        f"Max Frequency: {cpufreq.max:.2f}Mhz" + "\n" + \
        f"Min Frequency: {cpufreq.min:.2f}Mhz" + "\n\n"


# Memory Information
def get_ram_info():
    svmem = psutil.virtual_memory()

    return render_title("Memory Information") + "\n\n" + \
        f"Total: {get_size(svmem.total)}" + "\n\n"


# Disk Information
def get_disks_info():
    partitions = psutil.disk_partitions()
    disks = []
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that isn't ready
            continue

        disks.append(
            render_subtitle(f"Device: {partition.device}") + "\n" +
            f"  Mountpoint: {partition.mountpoint}" + "\n" +
            f"  File system type: {partition.fstype}" + "\n" +
            f"  Total Size: {get_size(partition_usage.total)}" + "\n" +
            f"  Used: {get_size(partition_usage.used)}" + "\n" +
            f"  Free: {get_size(partition_usage.free)}" + "\n" +
            f"  Percentage: {partition_usage.percent}%" + "\n"
        )

    return render_title("Disk Information") + "\n\n" + "\n".join(disks) + "\n"


# GPU information
def get_gpu_info():
    gpus = GPUtil.getGPUs()
    list_gpus = []
    for gpu in gpus:
        # get the GPU id
        gpu_id = gpu.id
        # name of GPU
        gpu_name = gpu.name
        # get % percentage of GPU usage of that GPU
        gpu_load = f"{gpu.load*100}%"
        # get free memory in MB format
        gpu_free_memory = f"{gpu.memoryFree}MB"
        # get used memory
        gpu_used_memory = f"{gpu.memoryUsed}MB"
        # get total memory
        gpu_total_memory = f"{gpu.memoryTotal}MB"
        # get GPU temperature in Celsius
        gpu_temperature = f"{gpu.temperature} °C"
        list_gpus.append(
            render_subtitle(f"GPU {gpu_id}") + "\n" +
            f"  Name: {gpu_name}" + "\n" +
            f"  Load: {gpu_load}" + "\n" +
            f"  Free memory: {gpu_free_memory}" + "\n" +
            f"  Used memory: {gpu_used_memory}" + "\n" +
            f"  Total memory: {gpu_total_memory}" + "\n" +
            f"  Temperature: {gpu_temperature}" + "\n"
        )

    return render_title("GPU Information") + "\n\n" + "\n".join(list_gpus)


class LoadingWindow(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.label = Label(self, text="\n\n" + " "*40 + " Analyzing System... " + " "*40 + "\n\n" + "Please wait!" + "\n\n")
        self.label.place(x=0, y=0)
        self.label.pack()
        self.pack(fill=BOTH, expand=1)

class Frames(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        for F in (LoadingWindow, SystemInfoWindow):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame(LoadingWindow)
        
    def show_frame(self, cont):
        self._frame = self.frames[cont]
        return self._frame.tkraise()

class SystemInfoWindow(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

    def set_text(self, text):
        text = Label(self, text=text)
        text.place(x=20, y=20)
        text.pack()


def center_frame(root: Frames):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = int((screen_width/2) - (root._frame.winfo_reqwidth()/2))
    y = int((screen_height/2) - (root._frame.winfo_reqheight()/2))
    
    root.geometry(f"+{x}+{y}")

def load_system_info_window(root: Frames):
    system_info = get_base_system_info() + get_cpu_info() + \
        get_ram_info() + get_disks_info() + get_gpu_info()
    
    root.show_frame(SystemInfoWindow)
    root._frame.set_text(system_info)
    
    center_frame(root)
    
    
if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    
    root = Frames()
    root.wm_title("System Information")
    center_frame(root)
    
    thread = Thread(target=load_system_info_window, args=(root,))
    thread.start()
    root.resizable(False, False)
    root.mainloop()
    
