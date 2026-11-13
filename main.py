import argparse
import os

from dotenv import load_dotenv
from openai import OpenAI

from call_function import available_functions, call_function
from prompts import system_prompt


def main(api_key: str):
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--working-directory",
        default="./calculator",
        help="Directory containing the project to work on (default: ./calculator)",
    )
    args = parser.parse_args()
    if not os.path.isdir(args.working_directory):
        parser.error(f"Working directory does not exist: {args.working_directory}")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    for _ in range(20):
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,  # pyright: ignore[reportArgumentType]
            temperature=0.2,
            tools=available_functions,
        )
        if not response.choices:
            raise RuntimeError("The agent returned no response choices.")
        message = response.choices[0].message
        messages.append(message)
        if not message.tool_calls:
            if message.content is None:
                raise RuntimeError("The agent returned an empty response.")
            print(message.content)
            return
        for tool_call in message.tool_calls:
            if tool_call.type != "function":
                raise RuntimeError(f"Unsupported tool call type: {tool_call.type}")
            result_message = call_function(
                tool_call, verbose=args.verbose, working_directory=args.working_directory
            )
            messages.append(result_message)
            if args.verbose:
                print(f"-> {result_message['content']}")
    raise RuntimeError("Maximum iterations reached before the agent finished.")

if __name__ == "__main__":
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER api not found")
    main(api_key)
