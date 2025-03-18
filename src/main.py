import argparse

from generator import MinecraftVersion, Platform, Language, Generator

parser = argparse.ArgumentParser(description="Valkyrien Template Generator")
parser.add_argument("--mod-name", type=str, default="Example Mod", help="the human-readable name of your addon")
parser.add_argument("--mc-version", type=MinecraftVersion, default=MinecraftVersion.v1201, help="the Minecraft version of your addon")
parser.add_argument("--mod-id", type=str, default=None, help="the Mod ID of your addon")
parser.add_argument("--package", type=str, default="com.example", help="the unique package name for your addon")
parser.add_argument("--platform", type=Platform, default=Platform.ARCHITECTURY, help="the platform on which you will test and release the addon")
parser.add_argument("--language", type=Language, default=Language.JAVA, help="the language being used to write the addon")

def main():
    args = parser.parse_args()

    mod_name = args.mod_name
    mc_version = args.mc_version
    mod_id = args.mod_id
    package = args.package
    platform = args.platform
    language = args.language

    gen = Generator(mod_name, mc_version, mod_id, package, platform, language)

main()