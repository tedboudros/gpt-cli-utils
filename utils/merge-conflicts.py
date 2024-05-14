import subprocess
import os
import openai
import json
import click
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def get_system_prompt(merge_from, merge_to):
    return f"""You are a staff software engineer resolving merge conflicts in a git repository.
You are merging from {merge_from} to {merge_to}.
You will be looking at one file at a time.
Make sure you always resolve the conflicts and write out the whole file.
If you don't have enough information to resolve the conflict, you can ask me for more info, without outputting the file.
You can take a look on any file you want inside the project using the provided tool, but cross reference your findings with the user.
Always wrap your file output with triple backticks (```),
without type annotations like ```python, ```json, etc (REALLY IMPORTANT),
to ensure the file is formatted correctly.

SUPER IMPORTANT RULES:
- NEVER ASSUME ANY MISSING DETAILS, INSTEAD OUTLINE THE CONFUSION, AND ALWAYS ASK SIMPLE QUESTIONS TO FIND OUT. LOOK AT OTHER FILES FIRST IF IT HELPS MAKE THE QUESTIONS SIMPLER, BUT ALWAYS ASK QUESTIONS.
- NEVER MERGE CONFLICTS WITHOUT BEING SURE ABOUT THE INTENDED FUNCTIONALITY BEHIND THEM. YOU'RE REQUIRED TO ASK FOR INPUT.
- PAY ATTENTION TO THE NOTES FROM THE PREVIOUS CONVERSATION. THEY MIGHT CONTAIN REALLY IMPORTANT CONTEXT TO THE CURRENT FILE. DON'T GENERALISE THE INFORMATION PROVIDED IN THE NOTES, EXCEPT IF THE USER STATES SO.
- When you're able to resolve the conflicts, you must output the whole file, not just the conflict resolution section.
- When you're able to resolve the conflicts, use plain triple backticks (```) WITHOUT TYPE ANNOTATIONS to wrap the file content.
- When you're not able to resolve the conflicts, you must ask for more information without outputting the file.
- You can view other files in the project to help you resolve the conflicts, but you must cross reference your findings with the user.
- When printing the full file, instead of saying something along the lines of "Here is the resolved file:", you should exactly say "Updating the file!" and then print the full file.
"""


def get_merge_conflicts():
    try:
        result = subprocess.run(['git', 'ls-files', '-u'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print("Error running git command: ", result.stderr)
            return []

        conflicts = set()
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) == 4:
                file_path = parts[3]
                conflicts.add(file_path)

        conflicted_files = []
        for conflict in conflicts:
            try:
                with open(conflict, 'r') as file:
                    content = file.read()
                    conflicted_files.append({"filename": conflict, "content": content})
            except Exception as e:
                print(f"Error reading file {conflict}: {e}")
        return conflicted_files

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def merge_conflicted_file(file, merge_from, merge_to, merge_notes, messages=[]):
    print("-" * 80)
    print(f"Checking: {file['filename']}")

    tools = [
        {
            "type": "function",
            "function": {
              "name": "view_file_contents",
              "description": "If you have doubts about another file's contents, you can view it here.",
              "parameters": {
                "type": "object",
                "properties": {
                  "filename": {
                    "type": "string",
                    "description": "The name of the file you want to view, fetched from the same directory as the conflicted file (relative path).",
                  }
                },
                "required": ["filename"],
              },
            }
        }
    ]

    if not messages:
        messages = [
            {
                'role': 'system',
                'content': get_system_prompt(merge_from, merge_to)
            },
            {
                'role': 'user',
                'content': f"{file['filename']}\n```{file['content']}```"
            }
        ]
        if merge_notes and merge_notes != "":
            messages.append({
                'role': 'assistant',
                'content': f"Notes from our previous conversation about this merge:\n{merge_notes}"
            })
    response = openai.chat.completions.create(
        model='gpt-4o',
        temperature=0.4,
        max_tokens=4096,
        messages=messages,
        tools=tools
    )
    try:
        if 'Updating the file!' not in response.choices[0].message.content:
            raise Exception("The assistant didn't resolve the conflict.")
        content = "\n".join(response.choices[0].message.content.split('```')[1].split('\n')[1:]).split('```')[0]
        print("-" * 80)
        print("\n".join(response.choices[0].message.content.split('```')[0].split('\n')[:-1]))
        return content, messages
    except:
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call.function.name == 'view_file_contents':
                filename = json.loads(tool_call.function.arguments)['filename']
                if filename == file['filename']:
                    messages.append({
                        'role': 'assistant',
                        'content': f"ERROR: You can't view the same file you're resolving a conflict in."
                    })
                    return merge_conflicted_file(file, merge_from, merge_to, merge_notes, messages=messages)
                try:
                    with open(filename, 'r') as f:
                        content = f.read()
                        print("-" * 80)
                        print(f"Viewing: {filename}")
                        messages.append({
                            'role': 'assistant',
                            'content': f"FILE:\n```{content}```"
                        })
                        messages.append({
                            'role': 'assistant',
                            'content': f"FILE:\n```{content}```"
                        })
                        return merge_conflicted_file(file, merge_from, merge_to, merge_notes, messages=messages)
                except Exception as e:
                    messages.append({
                        'role': 'assistant',
                        'content': f"ERROR: reading file {filename} - {e}"
                    })
                    return merge_conflicted_file(file, merge_from, merge_to, merge_notes, messages=messages)

        response = response.choices[0].message.content
        if not response:
            return merge_conflicted_file(file, merge_from, merge_to, merge_notes, messages=messages)
        print("=" * 80)
        print(response)
        human_response = input("> ")
        if human_response == "exit":
            return
        messages.append({
            'role': 'assistant',
            'content': response
        })
        messages.append({
            'role': 'user',
            'content': human_response
        })
        return merge_conflicted_file(file, merge_from, merge_to, merge_notes, messages=messages)


@click.command()
@click.option('--merge-from', default='branch-A', help='Text description of the branch to merge from.')
@click.option('--merge-to', default='branch-B', help='Text description of the branch to merge to.')
def main(merge_from, merge_to):
    if not os.path.isdir('.git'):
        print("This script must be run inside a git repository.")
    else:
        files = get_merge_conflicts()
        merge_notes = ""
        if files:
            for file in files:
                new_contents, new_messages = merge_conflicted_file(file, merge_from, merge_to, merge_notes)
                user_replies = [message for message in new_messages if message['role'] == 'user'][1:]
                for reply in user_replies:
                    # find index of the user reply in the new_messages list
                    index = new_messages.index(reply)
                    merge_notes += f"\n{'-' * 80}\nAssistant: {new_messages[index-1]['content']}\n\nUser: {reply['content']}\n{'-' * 80}"
                print("-" * 80)
                print(f"Updated: {file['filename']}")
                with open(file['filename'], 'w') as f:
                    f.write(new_contents)
        else:
            print("No merge conflicts found.")


if __name__ == "__main__":
    main()
