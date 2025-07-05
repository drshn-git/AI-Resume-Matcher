import subprocess

def generate_reasoning(resume_text, job_description):
    prompt = f"""Compare the following RESUME and JOB DESCRIPTION and explain why the resume matches or doesn't match the job.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Explain the compatibility:"""

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        output = result.stdout.decode("utf-8")
        return output.strip()
    except Exception as e:
        return f"⚠️ Error generating explanation: {str(e)}"
