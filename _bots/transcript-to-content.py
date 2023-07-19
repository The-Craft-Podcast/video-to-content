import os
import openai
import json
import yaml

# Retrieve your API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-4"

# Define function call for GPT-4
def create_function_call_message(function_name, messages, functions):
    '''Create a function call message for GPT-4 to process'''
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            functions=functions,
            function_call={"name": function_name},
        )
    except Exception as exception:
        print(exception.args)

    response_message = response["choices"][0]["message"]

    print(response_message["function_call"]["arguments"])
    function_args = json.loads(response_message["function_call"]["arguments"])

    return function_args

def process_transcript(raw_transcript, format_notes, suggestions=None):
    '''Process raw transcript into a desired format, taking into account any corrections'''
    function_name = "process_transcript"

    messages = [
        {
            "role": "user",
            "content": f"Help me clean up and organize the following transcript. Please follow these guidelines:\n{format_notes}\n{suggestions}\n\nThe raw transcript:\n\n{raw_transcript}"
        },
    ]
    
    functions = [
        # Define function for GPT-4
        {
            "name": function_name,
            "description": "Process raw transcript into a desired format, taking into account any corrections",
            "parameters": {
                "type": "object",
                "properties": {
                    "transcript": {
                        "type": "array",
                        "items": {
                            "estimated-timestamp": {
                                "type": "string",
                                "description": "The estimated timestamp of the accompanying text. NEVER enclose in quotes. Format example: 00:00:00",
                            },
                            "speaker": {
                                "type": "string",
                                "description": "The name of the speaker. NEVER enclose in quotes. Format example: Lex",
                            },
                            "text": {
                                "type": "string",
                                "description": "What the speaker said. Try to remove filler words like 'uh' and 'um'. Reform the text into coherent sentences, but don't deviate from the speaker's original phrasing. Delete repeated words and stammering. NEVER enclose in quotes. Format example: 'Hello, world!'",
                            },
                        },
                    },
                    # "required": ["speaker", "estimated-timestamp", "text"],
                },
                "description": "Array of transcript objects that cover the entire conversation. Each object has a 'speaker' string, an 'estimated-timestamp' string, and a 'text' string.",
            },
            "required": ["transcript"],
        }
    ]
    function_args = create_function_call_message(function_name, messages, functions)
    return function_args

def process_notes(transcript, parameter_list, suggestions=None):
    '''Process raw notes into a desired format, taking into account any corrections'''
    function_name = "process_notes"

    messages = [
        {
            "role": "user",
            "content": f"Help me process the following transcript. Follow the descriptions in the {function_name} function precisely. Do not deviate!\n\nHere are any corrections I want to make from your previous attempts:\n{suggestions}.\nTranscript:\n\n{transcript}\n"
        }
    ]
    functions = [
        # Define function for GPT-4
        {
            "name": function_name,
            "description": "Process raw notes into a desired format, taking into account any corrections",
            "parameters": {
                "type": "object",
                "properties": {
                    # "episode-file-name": {
                    #     "type": "string",
                    #     "description": "A string in the format of 'YYYY-MM-DD-episode-##' based on the date and number of the episode. For example, '2023-01-17-episode-59'."
                    # },
                    "title": {
                        "type": "string",
                        "description": "A string that contains a unique and interesting episode name. Format example: Title of super cool episode",
                    },
                    "description": {
                        "type": "string",
                        "description": "A string that contains an intriguing, two tweet-long description based on the episode content.",
                    },
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {
                                    "type": "string",
                                    "description": "A string containing the timestamp of the chapter. Format example: 00:00:00",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Title for the section. Format example: This is a title",
                                },
                            },
                            "required": ["timestamp", "title"],
                        },
                        "description": "Array of section objects. Each object has 'timestamp' and 'title' strings. Timestamps are in the format of 00:00:00. Generate 5-10 sections based on the transcript.",
                    },
                    # "pubDate": {
                    #     "type": "string",
                    #     "description": "DDD, DD MM YYYY 18:00:00 -0500 # 6pm New York time",
                    # },
                    # "itunes-explicit": {
                    #     "type": "boolean",
                    #     "description": "Always false",
                    # },
                    # "itunes-episode": {
                    #     "type": "integer",
                    #     "description": "Episode number",
                    # },
                    # "itunes-episodeType": {
                    #     "type": "string",
                    #     "description": "Always 'Full'",
                    # },
                    # "youtube-full": {
                    #     "type": "string",
                    #     "description": "Input the proper YouTube link found in the notes. Do not enclose in quotes. Format example: https://www.youtube.com/watch?v=1234567890",
                    # },
                    # "discussion": {
                    #     "type": "string",
                    #     "description": "Input the proper wrap up Twitter link found in the notes. Do not enclose in quotes. Format example: https://twitter.com/lexfridman/status/1234567890",
                    # },
                    # "timeline": {
                    #     "type": "array",
                    #     "items": {
                    #         "type": "object",
                    #         "properties": {
                    #             "seconds": {
                    #                 "type": "integer",
                    #                 "description": "Timestamp in cumulative seconds. Do not enclose in quotes. Format example: 1234",
                    #             },
                    #             "title": {
                    #                 "type": "string",
                    #                 "description": "Title for the timestamp. Do not enclose in quotes. Format example: This is a title",
                    #             },
                    #         },
                    #         "required": ["seconds", "title"],
                    #     },
                    #     "description": "Array of timestamp objects. Each object has a 'seconds' integer and a 'title' string.",
                    # },
                    # "badges": {
                    #     "type": "array",
                    #     "items": {
                    #         "type": "object",
                    #         "properties": {
                    #             "type": {
                    #                 "type": "string",
                    #                 "description": "A string containing badge type. Currently all recipients recieve exactly stayed-to-end type badges. NEVER enclose in quotes. Format example: stayed-to-end",
                    #             },
                    #             "recipient": {
                    #                 "type": "string",
                    #                 "description": "A string containing ONLY the Twitter username of the badge recipient. ATTENTION:  Do not enclose in quotes (unless it is a numeric like 037) and NEVER include the @ symbol. Format example: dtedesco1. Do NOT EVER include the @ symbol!",
                    #             },
                    #         },
                    #         "required": ["type", "recipient"],
                    #     },
                    #     "description": "Array of badge objects. Each object has a 'type' string and a 'recipient' string. Recipient MUST NOT include the @ symbol.",
                    # },
                    "## Quick notes and links": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "note and/or link": {
                                    "type": "string",
                                    "quick note": "Markdown formatted bullet point containing a note and/or link. NEVER enclose in quotes. Format example: - See [FullDecent's quick non-transferrable ERC-721 implementation ('badges')](https://github.com/fulldecent/solidity-template/blob/main/contracts/Tokens/NonTransferrableERC721.sol) based on [Solmate](https://github.com/transmissions11/solmate) by [@transmissions11](https://twitter.com/transmissions11)",
                                },
                            },
                            "required": ["note and/or link"],
                        },
                        "description": "Array of enhanced show notes based on raw_notes. Enhance the notes by including hyperlinks for relevant entities that are mentioned inside. NEVER enclose in quotes. Don't include links to this episode's twitch stream, youtube video, or tweets--those are handled elsewhere.",
                    },
                    "## Wrap up tweets drafts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "tweet draft": {
                                    "type": "string",
                                    "description": "A wrap-up tweet for the episode either summarizing what was covered, asking an intriguing question relevant to the episode, sharing a hot take, asking for feedback, sharing a link, or a combination of these. Keep it exciting and engaging. Example:  'Is less validators bad? For some prior art we can always compare to @trondao which has only 27 super representatives.' Second example: 'Here is Episode 82—Cupcake Sister, checking out Ella's first NFT unboxing. I purchased it on the street in China from a vending machine. Is it legal in China? Let's find out!' Third example: 'Check out Remix at https://remix.ethereum.org and now I can see all this documentation that was always there. Here is where to find it… [[ PHOTO ]]'",
                                },
                            },
                            "required": ["tweet"],
                        },
                        "description": "Array of drafts for a wrap-up tweet thread. Each tweet should be modular, but the total array of tweets should cover the key and most interesting things covered in the episodes. Use the notes and timestamps for a reference of what to include.",
                    },
                    "## Wrap up LinkedIn post draft": {
                        "type": "string",
                        "description": "A wrap-up LinkedIn post for the episode either summarizing what was covered, asking an intriguing question relevant to the episode, sharing a hot take, asking for feedback, sharing a link, or a combination of these. Keep it exciting and engaging. These can be a bit longer than individual tweets and mention multiple topics, as long as it's done so in an organized fashion. Optimize for engagement on LinkedIn.",
                    },
                },
                "required": parameter_list
            },
        },
    ]

    function_args = create_function_call_message(function_name, messages, functions)
    return function_args



def main():
    '''Main function'''
    # User input parameters
    parameter_list = [
        "title",
        "description",
        "sections",
        "## Quick notes and links",
        "## Wrap up tweets drafts",
        "## Wrap up LinkedIn post draft",
    ]

    # Read the raw transcript from the file
    with open("raw-transcript.txt", "r") as raw_transcript_file:
        raw_transcript = raw_transcript_file.read()
        # Close the file
        raw_transcript_file.close()

    # # Get the parent directory of the current directory
    # parent_dir = os.path.dirname(os.getcwd())
    # # Get the path to the _drafts directory
    # drafts_dir = os.path.join(parent_dir, 'hour.gg/_drafts')
    # # Get an ordered list of all files in the _drafts directory
    # files = sorted(os.listdir(drafts_dir))
    # print(f'List of files in the _drafts directory (in order):\n{files}')

    # Loop over every file in the _drafts directory
    # for filename in files:

    # process_or_skip = input(f'\n\nUpdate, save, and exit notes doc for {filename}. Then, hit return. Or skip this file by entering "skip":  ')

    # # If the user wants to skip this file, then skip it
    # if process_or_skip == "skip":
    #     continue

    # Initialize suggestions as an empty string
    suggestions = ""

    # Loop until the user is satisfied with the result.
    while True:

        # Read the raw notes from the file
        with open("desired-output.md", "r") as desired_output_notes:
            desired_output_notes = desired_output_notes.read()

        # Process the transcript
        transcriptObj = process_transcript(raw_transcript, desired_output_notes, suggestions)

        # Call the function
        # result = process_notes(raw_notes, desired_output_format, parameter_list, suggestions)

        # Example results, for testing.
        # result = {'episode-file-name': '2023-02-07-episode-62', 'title': "'Soulbind'", 'description': "'In episode 62, we delve into the world of soulbound tokens. We discuss the proposed EIP-6049 and the mechanisms of Ethereum consensus changes. We also cover various concepts around these tokens such as EOA evaluation, attributes, personhood, and business models. Lastly, we explore the potential of soulbound tokens in ticketing.'", 'youtube-full': 'https://youtu.be/rlePJziAY6Y', 'discussion': 'https://twitter.com/fulldecent/status/1623232559147515904', 'timeline': [{'seconds': 0, 'title': 'Intro'}, {'seconds': 43, 'title': 'EIP-6049'}, {'seconds': 169, 'title': 'How do Eth consensus changes happen?'}, {'seconds': 518, 'title': 'Intro to Soulbind'}, {'seconds': 603, 'title': 'Existing standard for soulbound NFTs'}, {'seconds': 638, 'title': 'Can we standardize EOA evaluation?'}, {'seconds': 871, 'title': 'Attributes and personhood'}, {'seconds': 932, 'title': 'Business model and product interview'}, {'seconds': 1238, 'title': 'Mintable tokens and spam'}, {'seconds': 1304, 'title': 'Content moderation: keys = calls'}, {'seconds': 1350, 'title': 'Is burnable really soulbound?'}, {'seconds': 1383, 'title': 'Can SBT be mutable?'}, {'seconds': 1512, 'title': 'I Leveling up token'}, {'seconds': 1604, 'title': 'Ticketing'}], 'badges': [{'type': 'stayed-to-end', 'recipient': 'Rito_Rhymes'}, {'type': 'stayed-to-end', 'recipient': '037'}, {'type': 'stayed-to-end', 'recipient': 'exstalis'}, {'type': 'stayed-to-end', 'recipient': '0xrobrecht'}, {'type': 'stayed-to-end', 'recipient': 'cer_andrew'}, {'type': 'stayed-to-end', 'recipient': 'EllieVoxel'}, {'type': 'stayed-to-end', 'recipient': 'dtedesco1'}]}

        front_matter_new = yaml.dump(transcriptObj, sort_keys=False)
        print(f'\n\nYour transcript was processed.')

        output_file_path = f'_drafts/transcript.md'

        with open(output_file_path, "w") as output_file:
            output_file.write(f'{front_matter_new}')
            output_file.close()
            print(f'\n\nYour notes were saved to {output_file_path}')

        # Ask the user for any suggestions
        new_suggestions = input(f"\nUpate and save the notes files and enter any suggestions (or hit return once you're happy with the results): ")

        # If the user has no suggestions, append to the output file and exit
        if new_suggestions == "":
            break
        #     episode_file_name = result["episode-file-name"] + '.md'
        #     output_file_path = f'_drafts/{episode_file_name}'
        #     # Check that the output_file_name is the same as the target file_path
        #     # If exception is raised, alert the user that their output is not matched to the correct file
        #     # assert episode_file_name == filename, f'The notes you shared are for: {episode_file_name}, but you are trying to save to: {filename}'

        #     with open(output_file_path, "a") as output_file:
        #         print(f'\n\n{front_matter_new}')
        #         output_file.write(f'\n\n<!--\n\n{front_matter_new}\n\n-->')
        #         output_file.close()
        #         print(f'\n\nYour notes were saved to {output_file_path}')
        #     break

        # suggestions = new_suggestions + f'\n\nFor reference, your previous output was this: {result}'

        suggestions += new_suggestions

if __name__ == "__main__":
    main()
