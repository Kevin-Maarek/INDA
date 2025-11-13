import json
from typing import Dict, Any, Callable
from query_service.dsl.functions import DSL_FUNCTIONS

# run the DSL flow step-by-step
def execute_dsl_flow(dsl_plan: Dict[str, Any]) -> Any:

    print(f"starting DSL flow")

    context = None 
    steps = dsl_plan.get("steps", [])
    if not steps:
        raise ValueError("No steps found in DSL plan")

    for i, step in enumerate(steps):
        fn_name = step.get("fn")
        args = step.get("args", {})

        print(f"step {i+1}/{len(steps)}: {fn_name}({args})")

        # check if function exists
        if fn_name not in DSL_FUNCTIONS:
            raise ValueError(f"function '{fn_name}' not found in DSL_FUNCTIONS")

        fn: Callable = DSL_FUNCTIONS[fn_name]

        # get the context from previous step if needed 
        try:
            if context is not None:
                result = fn(context, **args)
            else:
                result = fn(**args)
        except TypeError:
            result = fn(**args)
        except Exception as e:
            print(f"error in {fn_name} {e}")
            raise e
        # save the context for the next step
        context = result 

    print(f"Flow executed successfully.")
    return context
