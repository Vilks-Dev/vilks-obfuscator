import ast
import random
import string
import base64
import hashlib

class Obfuscator:
    def __init__(self, code: str, level: str):
        self.code = code
        self.level = level
        self.renaming_map = {}
        self.defined_names = set()
        self.builtins = set(dir(__builtins__))

    def obfuscate(self) -> str:
        try:
            tree = ast.parse(self.code)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {e}")

        self._collect_definitions(tree)
        self._generate_renaming_map()

        if self.level in ["basic", "standard", "hardcore"]:
            tree = Minifier().visit(tree)
            tree = Renamer(self.renaming_map).visit(tree)
            tree = JunkCodeInjector().visit(tree)

        if self.level in ["standard", "hardcore"]:
            tree = BuiltinsObfuscator().visit(tree)
            tree = BooleanAndNoneObfuscator().visit(tree)
            tree = StringEncryptor().visit(tree)
            tree = IntegerSplitter().visit(tree)
            tree = OpaquePredicateInjector().visit(tree)
            tree = ControlFlowFlattener().visit(tree)

        if self.level == "hardcore":
            tree = TypeTreeObfuscator().visit(tree)       
            tree = AntiDecompilerInjector().visit(tree)    
            tree = DynamicImportObfuscator().visit(tree)

        ast.fix_missing_locations(tree)
        
        # Correction pour forcer l'unparser natif de Python beaucoup plus robuste avec les f-strings
        try:
            processed_code = ast.unparse(tree)
        except AttributeError:
            import astunparse
            processed_code = astunparse.unparse(tree)

        if self.level == "hardcore":
            return self._generate_ultimate_vm(processed_code)

        headers = []
        if self.level == "standard":
            headers.append("import base64\nimport random\nimport time")
            headers.append("x = random.randint(1, 1000) * 2")
            headers.append(self._get_decrypt_helper_code())
            processed_code = "\n".join(headers) + "\n" + processed_code

        return self._wrap_polymorphic(processed_code)

    def _collect_definitions(self, tree: ast.AST):
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not node.name.startswith("__") or not node.name.endswith("__"):
                    self.defined_names.add(node.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                if not node.id.startswith("__") or not node.id.endswith("__"):
                    self.defined_names.add(node.id)
            elif isinstance(node, ast.arg):
                if not node.arg.startswith("__") or not node.arg.endswith("__"):
                    self.defined_names.add(node.arg)

    def _generate_renaming_map(self):
        for name in self.defined_names:
            if name not in self.builtins and len(name) > 1:
                rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
                self.renaming_map[name] = f"_0x{rand_suffix}"

    def _get_decrypt_helper_code(self) -> str:
        return """def _0xdec(data):
    import base64
    decoded = base64.b64decode(data)
    return "".join(chr(b ^ 95) for b in decoded)
"""

    def _generate_ultimate_vm(self, clean_code: str) -> str:
        op_load, op_add, op_store = random.sample(range(10, 250), 3)
        
        raw_bytes = clean_code.encode("utf-8")
        key_stream = random.randint(30, 240)
        pixel_data = []
        
        for byte in raw_bytes:
            obfuscated_byte = byte ^ key_stream
            pixel_data.append(obfuscated_byte)
            key_stream = (key_stream + obfuscated_byte) & 0xFF
            
        for _ in range(random.randint(150, 400)):
            pixel_data.append(random.randint(0, 255))
            
        vm_real_id = random.randint(1, 3)
        vm_funcs = [f"_0xexecute_shield_{''.join(random.choices(string.ascii_lowercase, k=4))}" for _ in range(3)]
        
        time_lock_iterations = 80000
        initial_seed_value = random.randint(100, 500)
        correct_hash = initial_seed_value
        for _ in range(time_lock_iterations):
            correct_hash = (correct_hash ^ 12345) & 0xFFFF

        sabotage_payload = "global _environment_scope; _environment_scope = None; import os; [os.abort() for _ in range(1)]"

        vm_definitions = []
        for i, func_name in enumerate(vm_funcs):
            is_real = (i + 1 == vm_real_id)
            
            if is_real:
                body = f"""
    _lock_check = _seed_key
    for _ in range({time_lock_iterations}):
        _lock_check = (_lock_check ^ 12345) & 0xFFFF
    if _lock_check != {correct_hash}:
        {sabotage_payload}

    _extracted_buffer = bytearray()
    _current_key = _seed_key
    
    for _idx in range(len(_matrix_stream)):
        _pixel_val = _matrix_stream[_idx]
        _plain_char = _pixel_val ^ _current_key
        _extracted_buffer.append(_plain_char)
        _current_key = (_current_key + _pixel_val) & 0xFF
        
    _environment_scope = globals()
    _bytecode_source = bytes(_extracted_buffer)
    
    try:
        ctypes.memset(id(_extracted_buffer), 0, len(_extracted_buffer))
    except:
        pass
    del _extracted_buffer
    
    try:
        _runtime_engine = compile(_bytecode_source.decode('utf-8', errors='ignore'), '<quantum_core>', 'exec')
        try:
            ctypes.memset(id(_bytecode_source), 0, len(_bytecode_source))
        except:
            pass
        _0x_hb = time.time()
        getattr(__builtins__, 'exec')(_runtime_engine, _environment_scope)
    except Exception:
        _sys.exit(1)
"""
            else:
                body = f"""
    _fake_buffer = [x ^ random.randint(1, 254) for x in _matrix_stream[:50]]
    if len(_fake_buffer) > 0:
        {sabotage_payload}
"""
            
            vm_code_block = f"""
def {func_name}(_matrix_stream, _seed_key):
    global _0x_hb
    _clock = time.time()
    _sys = sys.modules.get('sys')
    
    if _sys.gettrace() is not None or (time.time() - _clock) > 0.03:
        {sabotage_payload}

    try:
        if platform.system() == "Windows":
            if ctypes.windll.kernel32.IsDebuggerPresent():
                {sabotage_payload}
        else:
            with open("/proc/self/status", "r") as _f:
                if "TracerPid:\\t0" not in _f.read():
                    {sabotage_payload}
    except:
        pass
    {body}
"""
            vm_definitions.append(vm_code_block)

        all_vms_code = "\n".join(vm_definitions)
        server_endpoint_hash = hashlib.sha256(b"https://licensing.internal.shield/v2").hexdigest()

        ultimate_vm_code = f"""import sys, time, ctypes, hashlib, platform, threading

_0x_hb = time.time()
_0x_mut_table = {{ "load": {op_load}, "add": {op_add}, "store": {op_store} }}
_0x_srv = "{server_endpoint_hash}"

def _0xwatchdog():
    global _0x_hb
    _sys = sys.modules.get('sys')
    while True:
        time.sleep(0.4)
        _now = time.time()
        if (_now - _0x_hb) > 1.2:
            {sabotage_payload}
        _0x_hb = _now
        
        try:
            if 'frida' in sys.modules or 'hook' in sys.modules:
                {sabotage_payload}
                
            if platform.system() == "Windows":
                if ctypes.windll.kernel32.IsDebuggerPresent():
                    {sabotage_payload}
            else:
                with open("/proc/self/status", "r") as _f:
                    if "TracerPid:\\t0" not in _f.read():
                        {sabotage_payload}
        except:
            pass

def _0x_request_remote_key(_token_payload):
    _static_fallback_key = {key_stream}
    _verification_scrypt = hashlib.sha256(_token_payload.encode('utf-8')).hexdigest()
    if not _verification_scrypt:
        return None
    return _static_fallback_key

{all_vms_code}

try:
    _wd_thread = threading.Thread(target=_0xwatchdog, daemon=True)
    _wd_thread.start()
except:
    pass

_fake_image_pixels = {list(pixel_data)}

_vm_selectors = {vm_funcs}
_target_vm_func = globals()[_vm_selectors[{vm_real_id - 1}]]
_target_vm_func(_fake_image_pixels, {initial_seed_value})
"""
        return self._wrap_polymorphic(ultimate_vm_code)

    def _wrap_polymorphic(self, code_to_wrap: str) -> str:
        key = random.randint(1, 255)
        encoded_bytes = bytes([b ^ key for b in code_to_wrap.encode("utf-8")])
        b64_str = base64.b64encode(encoded_bytes).decode("utf-8")
        
        v_func = f"_0xf_{''.join(random.choices(string.ascii_lowercase, k=4))}"
        v_data = f"_0xd_{''.join(random.choices(string.ascii_lowercase, k=4))}"
        v_key = f"_0xk_{''.join(random.choices(string.ascii_lowercase, k=4))}"
        v_bytes = f"_0xb_{''.join(random.choices(string.ascii_lowercase, k=4))}"
        v_unpacked = f"_0xu_{''.join(random.choices(string.ascii_lowercase, k=4))}"
        v_x = f"_0xx_{''.join(random.choices(string.ascii_lowercase, k=4))}"
        
        opaque_key_calc = f"({key ^ 42} ^ 42)"
        
        wrapper = f"""import base64
def {v_func}({v_data}, {v_key}):
    {v_bytes} = getattr(base64, 'b64decode')({v_data})
    {v_unpacked} = "".join(chr({v_x} ^ {v_key}) for {v_x} in {v_bytes})
    del {v_bytes}
    getattr(__builtins__, 'exec')({v_unpacked}, globals())
{v_func}(b"{b64_str}", {opaque_key_calc})
"""
        if self.level == "hardcore":
            marker = "# INTEGRITY: "
            wrapper_bytes = (wrapper + marker).encode("utf-8")
            sha = hashlib.sha256(wrapper_bytes).hexdigest()
            return wrapper + marker + sha + "\n"
        
        return wrapper

class Minifier(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.generic_visit(node)
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            node.body.pop(0)
        return node

    def visit_ClassDef(self, node: ast.ClassDef):
        self.generic_visit(node)
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            node.body.pop(0)
        return node

    def visit_Module(self, node: ast.Module):
        self.generic_visit(node)
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            node.body.pop(0)
        return node

class Renamer(ast.NodeTransformer):
    def __init__(self, renaming_map: dict):
        self.renaming_map = renaming_map

    def visit_Name(self, node: ast.Name):
        if node.id in self.renaming_map:
            node.id = self.renaming_map[node.id]
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name in self.renaming_map:
            node.name = self.renaming_map[node.name]
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef):
        if node.name in self.renaming_map:
            node.name = self.renaming_map[node.name]
        self.generic_visit(node)
        return node

    def visit_arg(self, node: ast.arg):
        if node.arg in self.renaming_map:
            node.arg = self.renaming_map[node.arg]
        return node

class JunkCodeInjector(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.generic_visit(node)
        if len(node.body) > 0:
            junk_var = f"_0xjunk_{random.randint(1000, 9999)}"
            junk_val = random.randint(1, 100)
            junk_node = ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.Constant(value=junk_val)
            )
            node.body.insert(0, junk_node)
        return node

# CORRECTION DU BUG AST : StringEncryptor ignore désormais les composants internes des f-strings
class StringEncryptor(ast.NodeTransformer):
    def __init__(self):
        self.inside_fstring = False

    def visit_JoinedStr(self, node: ast.JoinedStr):
        # On mémorise qu'on entre dans une f-string pour ne pas casser son sous-arbre AST
        old_state = self.inside_fstring
        self.inside_fstring = True
        self.generic_visit(node)
        self.inside_fstring = old_state
        return node

    def visit_Constant(self, node: ast.Constant):
        if self.inside_fstring:
            return node # Ne pas obfusquer les constantes de f-strings pour éviter l'erreur d'unparse
        
        if isinstance(node.value, str) and len(node.value) > 0:
            encrypted_str = self._encrypt_string(node.value)
            dec_call = ast.Call(
                func=ast.Name(id="_0xdec", ctx=ast.Load()),
                args=[ast.Constant(value=encrypted_str)],
                keywords=[]
            )
            return dec_call
        return node

    def _encrypt_string(self, s: str) -> str:
        s_bytes = s.encode("utf-8")
        xor_bytes = bytes([b ^ 95 for b in s_bytes])
        return base64.b64encode(xor_bytes).decode("utf-8")

class IntegerSplitter(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, int) and not isinstance(node.value, bool) and node.value > 0:
            val = node.value
            part1 = random.randint(1, max(2, val - 1))
            part2 = val - part1
            return ast.BinOp(
                left=ast.Constant(value=part1),
                op=ast.Add(),
                right=ast.Constant(value=part2)
            )
        return node

class BooleanAndNoneObfuscator(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, bool):
            if node.value is True:
                return ast.Compare(left=ast.Constant(value=1), ops=[ast.Eq()], comparators=[ast.Constant(value=1)])
            else:
                return ast.Compare(left=ast.Constant(value=1), ops=[ast.NotEq()], comparators=[ast.Constant(value=1)])
        elif node.value is None:
            return ast.Subscript(
                value=ast.List(elts=[], ctx=ast.Load()),
                slice=ast.Slice(lower=None, upper=None, step=None),
                ctx=ast.Load()
            )
        return node

class BuiltinsObfuscator(ast.NodeTransformer):
    def visit_Name(self, node: ast.Name):
        if node.id in ['print', 'eval', 'exec', 'open', 'len', 'range', 'str', 'int', 'globals', 'locals']:
            name_encoded = base64.b64encode(node.id.encode('utf-8')).decode('utf-8')
            return ast.Call(
                func=ast.Name(id='getattr', ctx=ast.Load()),
                args=[
                    ast.Call(func=ast.Name(id='__import__', ctx=ast.Load()), args=[ast.Constant(value='builtins')], keywords=[]),
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Call(
                                func=ast.Attribute(value=ast.Name(id='base64', ctx=ast.Load()), attr='b64decode', ctx=ast.Load()),
                                args=[ast.Constant(value=name_encoded)], keywords=[]
                            ),
                            attr='decode', ctx=ast.Load()
                        ),
                        args=[ast.Constant(value='utf-8')], keywords=[]
                    )
                ],
                keywords=[]
            )
        return node

class DynamicImportObfuscator(ast.NodeTransformer):
    def visit_Import(self, node):
        new_nodes = []
        for alias in node.names:
            name_bytes = alias.name.encode('utf-8')
            encoded = base64.b64encode(name_bytes).decode('utf-8')
            
            import_call = ast.Assign(
                targets=[ast.Name(id=alias.asname if alias.asname else alias.name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id='__import__', ctx=ast.Load()),
                    args=[
                        ast.Call(
                            func=ast.Attribute(
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id='base64', ctx=ast.Load()),
                                        attr='b64decode',
                                        ctx=ast.Load()
                                    ),
                                    args=[ast.Constant(value=encoded)],
                                    keywords=[]
                                ),
                                attr='decode',
                                ctx=ast.Load()
                            ),
                            args=[ast.Constant(value='utf-8')],
                            keywords=[]
                        )
                    ],
                    keywords=[]
                )
            )
            new_nodes.append(import_call)
        return new_nodes

    def visit_ImportFrom(self, node):
        if not node.module:
            return node
        new_nodes = []
        mod_bytes = node.module.encode('utf-8')
        mod_encoded = base64.b64encode(mod_bytes).decode('utf-8')
        
        temp_mod_name = f"_mod_{''.join(random.choices(string.ascii_lowercase, k=8))}"
        
        import_mod = ast.Assign(
            targets=[ast.Name(id=temp_mod_name, ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id='__import__', ctx=ast.Load()),
                args=[
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id='base64', ctx=ast.Load()),
                                    attr='b64decode',
                                    ctx=ast.Load()
                                ),
                                args=[ast.Constant(value=mod_encoded)],
                                keywords=[]
                            ),
                            attr='decode',
                            ctx=1
                        ),
                        args=[ast.Constant(value='utf-8')],
                        keywords=[]
                    )
                ],
                keywords=[]
            )
        )
        new_nodes.append(import_mod)
        
        for alias in node.names:
            target_name = alias.asname if alias.asname else alias.name
            get_attr = ast.Assign(
                targets=[ast.Name(id=target_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id='getattr', ctx=ast.Load()),
                    args=[
                        ast.Name(id=temp_mod_name, ctx=ast.Load()),
                        ast.Constant(value=alias.name)
                    ],
                    keywords=[]
                )
            )
            new_nodes.append(get_attr)
        return new_nodes

class AntiDecompilerInjector(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.generic_visit(node)
        anti_decomp_node = ast.If(
            test=ast.Compare(left=ast.Constant(value=0), ops=[ast.Eq()], comparators=[ast.Constant(value=1)]),
            body=[
                ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id='exec', ctx=ast.Load()),
                        args=[ast.Constant(value='def break_decompiler(): pass\nreturn break_decompiler')],
                        keywords=[]
                    )
                )
            ],
            orelse=[]
        )
        node.body.insert(0, anti_decomp_node)
        return node

class TypeTreeObfuscator(ast.NodeTransformer):
    def visit_ClassDef(self, node: ast.ClassDef):
        self.generic_visit(node)
        meta_node = ast.Assign(
            targets=[ast.Name(id='__qualname__', ctx=ast.Store())],
            value=ast.Constant(value=f"_0xclass_{''.join(random.choices(string.ascii_lowercase, k=4))}")
        )
        node.body.insert(0, meta_node)
        return node

class OpaquePredicateInjector(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        new_body = []
        for stmt in node.body:
            new_body.append(stmt)
            if isinstance(stmt, (ast.Assign, ast.Expr)) and random.random() < 0.3:
                opaque_cond = ast.Compare(
                    left=ast.BinOp(
                        left=ast.BinOp(left=ast.Name(id='x', ctx=ast.Load()), op=ast.Pow(), right=ast.Constant(value=2)),
                        op=ast.Mod(),
                        right=ast.Constant(value=4)
                    ),
                    ops=[ast.NotEq()],
                    comparators=[ast.Constant(value=2)]
                )
                junk = ast.Assign(
                    targets=[ast.Name(id=f"_jk_{''.join(random.choices(string.ascii_lowercase, k=5))}", ctx=ast.Store())],
                    value=ast.Constant(value=random.randint(1, 100))
                )
                opaque_if = ast.If(test=opaque_cond, body=[junk], orelse=[])
                new_body.append(opaque_if)
        node.body = new_body
        return node

class ControlFlowFlattener(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.generic_visit(node)
        if len(node.body) <= 1:
            return node

        new_body = []
        state_var = f"_0xstate_{random.randint(1000, 9999)}"
        states = list(range(1, len(node.body) + 1))
        
        init_state = ast.Assign(
            targets=[ast.Name(id=state_var, ctx=ast.Store())],
            value=ast.Constant(value=1)
        )
        new_body.append(init_state)

        if_cases = []
        for idx, stmt in enumerate(node.body):
            curr_state = states[idx]
            next_state = states[idx + 1] if idx + 1 < len(states) else 0

            state_update = ast.Assign(
                targets=[ast.Name(id=state_var, ctx=ast.Store())],
                value=ast.Constant(value=next_state)
            )

            case_body = []
            if isinstance(stmt, ast.Return):
                case_body.append(stmt)
            else:
                case_body.extend([stmt, state_update])

            case_test = ast.Compare(
                left=ast.Name(id=state_var, ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Constant(value=curr_state)]
            )
            if_cases.append((case_test, case_body))

        loop_body = None
        for test, body in reversed(if_cases):
            if loop_body is None:
                loop_body = ast.If(test=test, body=body, orelse=[])
            else:
                loop_body = ast.If(test=test, body=body, orelse=[loop_body])

        while_loop = ast.While(
            test=ast.Compare(
                left=ast.Name(id=state_var, ctx=ast.Load()),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(value=0)]
            ),
            body=[loop_body],
            orelse=[]
        )

        new_body.append(while_loop)
        node.body = new_body
        return node