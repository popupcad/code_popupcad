Installing Windows Compiler
================

Here's the steps:

    Download and install specifically Visual Studio C++ 2008 Express Edition.

http://download.microsoft.com/download/A/5/4/A54BADB6-9C3F-478D-8657-93B3FC9FE62D/vcsetup.exe

    Update for x64 Compilers: By default this will only give you a 32-bit compiler. I learned (from here and here) that you can download specifically the Windows SDK for Windows 7 and .NET Framework 3.5 SP1 which gives you a x64 compiler for VC++ 2008 (VC++ 9.0) if you need it. Just when you are installed it, you can uncheck everything except Developer Tools >> Visual C++ Compilers which will keep you from installing all the extra SDK tools that you may not need.

http://www.microsoft.com/en-us/download/details.aspx?id=3138

    tl;dr: If you want the x64 compilers for VC++ 2008, download specifically the Windows SDK for Windows 7 and .NET Framework 3.5 SP1 and uncheck everything except Developer Tools >> Visual C++ Compilers during install.

    Note: If you have both a 32- and 64-bit Python installation, you may also want to use virtualenv to create separate Python environments to use one or the other at a time without messing with your path to choose which Python version to use.

    Open up a cmd.exe

    Before you try installing something which requires C extensions, run the following batch file to load the VC++ compiler's environment into the session (i.e. environment variables, the path to the compiler, etc).

    Execute:

        32-bit Compilers:

        Note: 32-bit Windows installs will only have C:\Program Files\ as expected

            "C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\Tools\vsvars32.bat"
"c:\program files (x86)\microsoft visual studio 9.0\vc\bin\vcvarsxx.bat" works  in my case.
        64-bit Compilers:

            "C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\Tools\vsvars64.bat"

        Note: Yes, the native 64-bit compilers are in Program Files (x86). Don't ask me why.
        Additionally, if you are wondering what the difference between vcvars64.bat and vcvarsx86_amd64.bat or more importantly the difference between amd64 and x86_amd64, the former are for the native 64-bit compiler tools and the latter are the 64-bit cross compilers that can run on a 32-bit Windows installation.

    Update:
    If for some reason you are getting error: ... was unexpected at this time. where the ... is some series of characters, then you need to check that you path variable does not have any extraneous characters like extra quotations or stray characters. The batch file is not going to be able to update your session path if it can't make sense of it in the first place.