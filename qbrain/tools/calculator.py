from .base_tool import BaseTool, ToolResult
import ast
import operator


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Safely evaluate mathematical expressions"
    parameters = {
        "expression": {"type": "string", "description": "Math expression to evaluate"},
    }
    
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    def execute(self, expression: str) -> ToolResult:
        try:
            result = self._safe_eval(expression)
            return ToolResult(success=True, data={
                "expression": expression,
                "result": result,
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _safe_eval(self, expr: str):
        node = ast.parse(expr, mode="eval")
        return self._eval_node(node.body)
    
    def _eval_node(self, node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type in self.SAFE_OPERATORS:
                return self.SAFE_OPERATORS[op_type](left, right)
            raise ValueError(f"Unsupported operator: {op_type}")
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in self.SAFE_OPERATORS:
                return self.SAFE_OPERATORS[op_type](operand)
            raise ValueError(f"Unsupported operator: {op_type}")
        else:
            raise ValueError(f"Unsupported expression: {ast.dump(node)}")
