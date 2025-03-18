from enum import Enum
import os
import shutil
from jproperties import Properties
import zipfile

class MinecraftVersion(Enum):
    v1211 = "1.21.1"
    v1201 = "1.20.1"
    v1182 = "1.18.2"

class Platform(Enum):
    FORGE = "forge"
    FABRIC = "fabric"
    NEOFORGE = "neoforge"
    ARCHITECTURY = "architectury"

class Language(Enum):
    JAVA = "java"
    KOTLIN = "kotlin"

class Generator:
    def __init__(self, mod_name="Example Mod", mc_version=MinecraftVersion.v1201, mod_id=None, package="com.example", platform=Platform.ARCHITECTURY, language=Language.JAVA):
        self.mod_name = mod_name
        self.mc_version = mc_version
        self.mod_id = mod_id
        if not self.mod_id:
            self.mod_id = "_".join(mod_name.lower().split(" "))
        self.package = package
        self.platform = platform
        self.language = language

        self.output_loc = "output"

        self._validate_mod_id()
        self._validate_platform_and_version()

        print("==============Starting Generator===============")
        print(f"Mod Name: {self.mod_name}")
        print(f"Mod ID: {self.mod_id}")
        print(f"Package: {self.package}")
        print(f"Minecraft Version: {self.mc_version.value}")
        print(f"Platform: {self.platform}")
        print(f"Language: {self.language}")
        print("===============================================")

        self._clear_old_cache()
        path = self._does_template_exist()
        Generator.copy_over_template(path, "temp")
        self.change_directory_and_file_names_recursive("temp")
        self.zip_output()
        
    def _validate_mod_id(self):
        print("Validating Mod ID...")
        if (len(self.mod_id) < 2 or len(self.mod_id) > 64):
            print("Mod ID length must be between 2 and 64!")
            os._exit(1)
        print("Mod ID is valid!")
    
    def _validate_platform_and_version(self):
        print("Validating Platform and Minecraft version combination...")
        if self.platform == Platform.NEOFORGE and self.mc_version != MinecraftVersion.v1211:
            print("Current NeoForge template only supports 1.21.1!")
            os._exit(1)
        if self.platform == Platform.FORGE and self.mc_version == MinecraftVersion.v1211:
            print("Forge support is dropped past 1.20.1!")
            os._exit(1)
        print("Platform and Minecraft version are valid!")

    def _clear_old_cache(self):
        print("Deleting old cache...")
        if os.path.exists(self.output_loc):
            shutil.rmtree(self.output_loc)
        if os.path.exists("temp"):
            shutil.rmtree("temp")
    
    def _does_template_exist(self):
        print("Checking for correct template...")
        path = f"templates/{self.language.value}/{self.platform.value}"
        if self.platform == Platform.ARCHITECTURY:
            if self.mc_version == MinecraftVersion.v1211:
                path += "/neoforge"
            else:
                path += "/forge"
        if not os.path.exists(path):
            print(f"No templates exist at '{path}'")
            os._exit(1)
        return path
    
    def copy_over_template(source, destination):
        files = os.listdir(source)
        print(f"\tCreating new {destination} directory...")
        os.mkdir(destination)
        for file in files:
            if os.path.isfile(f"{source}/{file}"):
                print(f"Copying over {source}/{file}")
                shutil.copy(f"{source}/{file}", f"{destination}/{file}")
            else:
                Generator.copy_over_template(os.path.join(source, file), os.path.join(destination, file))
    
    def change_directory_and_file_names_recursive(self, dir_path_content):
        directories = os.listdir(dir_path_content)
        for directory in directories:
            if os.path.isfile(f"{dir_path_content}/{directory}"):
                if directory.startswith("example_mod") and directory != directory.replace('example_mod', self.mod_id):
                    print(f"\tChanging {dir_path_content}/{directory} to {dir_path_content}/{directory.replace('example_mod', self.mod_id)}")
                    shutil.copy(f"{dir_path_content}/{directory}", f"{dir_path_content}/{directory.replace('example_mod', self.mod_id)}")
                    os.remove(f"{dir_path_content}/{directory}")
                elif directory.startswith("ExampleMod") and directory != directory.replace('ExampleMod', ''.join(self.mod_name.split(' '))):
                    print(f"\tChanging {dir_path_content}/{directory} to {dir_path_content}/{directory.replace('ExampleMod', ''.join(self.mod_name.split(' ')))}")
                    shutil.copy(f"{dir_path_content}/{directory}", f"{dir_path_content}/{directory.replace('ExampleMod', ''.join(self.mod_name.split(' ')))}")
                    os.remove(f"{dir_path_content}/{directory}")
            else:
                if directory == "com" and os.path.exists(f"{dir_path_content}/{directory}/example"):
                    new_directory = f"{dir_path_content}/{self.package.replace('.', '/')}"
                    if new_directory == f"{dir_path_content}/{directory}/example":
                        continue
                    print(f"\tChanging {dir_path_content}/{directory}/example to {new_directory}")
                    shutil.copytree(f"{dir_path_content}/{directory}/example", new_directory, dirs_exist_ok=True)
                    shutil.rmtree(f"{dir_path_content}/{directory}")
        
        directories = os.listdir(dir_path_content)
        for directory in directories:
            path = f"{dir_path_content}/{directory}"
            if os.path.isfile(path):
                self.change_content_in_file(path)
            else:
                self.change_directory_and_file_names_recursive(path)
    
    def change_content_in_file(self, path):
        print(f"\t\tAdding Content to {path}...")

        if path.endswith(".properties"):
            self.change_content_in_gradle_properties(path)
            return
        
        if path.endswith(".jar"):
            return
        
        content = None
        with open(path, 'r') as f:
            content = f.read()
            f.close()

        if content is not None:
            content = content.replace("com.example", self.package)
            content = content.replace("ExampleMod", "".join(self.mod_name.split(" ")))
            content = content.replace("example_mod", self.mod_id)
            content = content.replace(r"{{ Mod ID }}", self.mod_id)
            content = content.replace(r"{{ Mod Name }}", self.mod_name)
            content = content.replace(r"{{ MC Version }}", self.mc_version.value)
            content = content.replace(r"{{ Arch API Version }}", self.get_arch_api_version())
            content = content.replace(r"{{ Fabric Loader Version }}", self.get_fabric_loader_version())
            content = content.replace(r"{{ Fabric API Version }}", self.get_fabric_api_version())
            content = content.replace(r"{{ Forge Version }}", self.get_forge_version())
            if self.mc_version != MinecraftVersion.v1211:
                content = content.replace(r"{{ Forge Version Short }}", self.get_forge_version().split("-")[1].split(".")[0])
            else:
                content = content.replace(r"{{ NeoForge Version Short }}", "4")
        
        with open(path, 'w') as f:
            f.write(content)
            f.close()
    
    def change_content_in_gradle_properties(self, path):
        configs = Properties()
        with open(path, 'rb') as f:
            configs.load(f)

            if configs.get("maven_group"):
                configs["maven_group"] = self.package
            if configs.get("archives_name"):
                configs["archives_name"] = self.mod_id
            if configs.get("minecraft_version"):
                configs["minecraft_version"] = self.mc_version.value
            if configs.get("architectury_api_version"):
                configs["architectury_api_version"] = self.get_arch_api_version()
            if configs.get("fabric_loader_version"):
                configs["fabric_loader_version"] = self.get_fabric_loader_version()
            if configs.get("fabric_api_version"):
                configs["fabric_api_version"] = self.get_fabric_api_version()
            if configs.get("forge_version"):
                configs["forge_version"] = self.get_forge_version()
            if configs.get("neoforge_version"):
                configs["neoforge_version"] = self.get_forge_version()
            
            f.close()
        
        with open(path, 'wb') as f:
            configs.store(f)
            f.close()
    
    def zip_output(self):
        print("Creating output/template.zip...")
        if not os.path.exists("output"):
            os.mkdir("output")

        with zipfile.ZipFile('output/template.zip', 'w') as myzip:
            self.zip_output_recursive("temp", myzip)
        shutil.rmtree("temp")
    
    def zip_output_recursive(self, dir_path, zip):
        directories = os.listdir(dir_path)
        for directory in directories:
            path = f"{dir_path}/{directory}"
            if os.path.isfile(path):
                zip.write(path, path[4:])
            else:
                self.zip_output_recursive(path, zip)
    
    def get_arch_api_version(self):
        match self.mc_version:
            case MinecraftVersion.v1182:
                return "4.12.94"
            case MinecraftVersion.v1201:
                return "9.2.14"
            case MinecraftVersion.v1211:
                return "13.0.8"
    
    def get_fabric_loader_version(self):
        match self.mc_version:
            case MinecraftVersion.v1182:
                return "0.16.10"
            case MinecraftVersion.v1201:
                return "0.16.10"
            case MinecraftVersion.v1211:
                return "0.16.10"
    
    def get_fabric_api_version(self):
        match self.mc_version:
            case MinecraftVersion.v1182:
                return "0.77.0+1.18.2"
            case MinecraftVersion.v1201:
                return "0.92.4+1.20.1"
            case MinecraftVersion.v1211:
                return "0.115.2+1.21.1"

    def get_forge_version(self):
        match self.mc_version:
            case MinecraftVersion.v1182:
                return "1.18.2-40.2.26"
            case MinecraftVersion.v1201:
                return "1.20.1-47.3.12"
            case MinecraftVersion.v1211:
                return "21.1.84"