def truncate_context(messages, max_messages=20):
    # messages[0] is always the system prompt from view_for - always keep it.
    # After that, only keep the last max_messages messages.
    if len(messages) <= max_messages + 1:
        return messages  # nothing to trim yet

    system_prompt = messages[0]
    recent_messages = messages[-max_messages:]
    trimmed_count = len(messages) - 1 - max_messages

    # Log every time we actually cut something, so a long run's compressions
    # show up in the console (the brief asks for this to be logged).
    print(f"[context] trimmed {trimmed_count} old message(s), keeping last {max_messages}")

    return [system_prompt] + recent_messages
