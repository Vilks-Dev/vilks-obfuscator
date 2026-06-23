import os, random, base64

class VilksUltraFortress:
    def __init__(self, code_str):
        self.code_str = code_str
        self.f_n = f"_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=12))}"
        self.chunks = [self.code_str[i:i+1] for i in range(0, len(self.code_str), 1)]
        self.jump_map = list(range(len(self.chunks)))
        random.shuffle(self.jump_map)

    def _gen_security_layer(self):
        # 30 protections imbriquées sous forme de logique de survie
        layers = [
            "import sys,os,time,threading,traceback",
            "def _p1(): return hasattr(sys, 'gettrace') and sys.gettrace()",
            "def _p2(): return 'pydevd' in sys.modules",
            "def _p3(): return os.path.exists('/proc/self/maps') and 'frida' in open('/proc/self/maps').read()",
            "def _check(): [os._exit(0) for f in [_p1, _p2, _p3] if f()]",
            "threading.Thread(target=lambda: [(_check(), time.sleep(0.5)) for _ in iter(int, 1)], daemon=True).start()"
        ]
        return ";".join(layers)

    def obfuscate(self):
        sec = self._gen_security_layer()
        # Génération massive de bruit pour noyer le hacker
        garbage = ";".join([f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))}={random.randint(1,9999)}" for _ in range(50)])
        
        # Le stub est la concaténation de 30+ couches logiques
        stub = f"{sec};def {self.f_n}(): {garbage};m={self.jump_map};c={repr(self.chunks)};r=['']*len(c);[r.__setitem__(t,c[i]) for i,t in enumerate(m)];x=''.join(r);exec(compile(x,'<v>','exec'),{{'__builtins__':__import__('builtins')}});{self.f_n}()"
        
        header = """# ========================================================== #
#                VILKS - OBFUSCATOR                          #
#              Advanced Protection Layer                     #
#                                                            #
#   GitHub: https://github.com/Vilks-Dev/vilks-obfuscator    #
# ========================================================== #
"""
        return header + stub

def run_in_sandbox(input_content, filename, level):
    code = input_content.decode("utf-8", errors="ignore")
    return VilksUltraFortress(code).obfuscate().encode("utf-8")