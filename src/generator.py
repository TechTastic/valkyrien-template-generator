from enum import Enum
import os
import shutil

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
        Generator.copy_over_template(path, "output")
        
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
        print(f"Creating new {destination} directory...")
        os.mkdir(destination)
        for file in files:
            if os.path.isfile(f"{source}/{file}"):
                print(f"Copying over {source}/{file}")
                shutil.copy(f"{source}/{file}", f"{destination}/{file}")
            else:
                Generator.copy_over_template(os.path.join(source, file), os.path.join(destination, file))