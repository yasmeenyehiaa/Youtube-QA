from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

client = Client()
dataset = client.create_dataset(dataset_name="youtube-qa-golden")

client.create_examples(
    dataset_id=dataset.id,
    examples=[
        # SLHCfIUTYZI
        {
            "inputs": {
                "question": "What is data streaming?",
                "video_id": "SLHCfIUTYZI",
            },
            "outputs": {
                "answer": "Data streaming is the continuous flow of data as it's generated from a source so that it can be used for real-time processing and analytics",
                "evidence": "[0:15] Data streaming is the continuous flow of data as it's generated from a source so that it can be used for real-time processing and analytics",
            },
        },
        {
            "inputs": {
                "question": "What is the meaning of data streaming?",
                "video_id": "SLHCfIUTYZI",
            },
            "outputs": {
                "answer": "Data streaming is the continuous flow of data as it's generated from a source so that it can be used for real-time processing and analytics",
                "evidence": "[0:15] Data streaming is the continuous flow of data as it's generated from a source so that it can be used for real-time processing and analytics",
            },
        },
        {
            "inputs": {
                "question": "What is machine learning?",
                "video_id": "SLHCfIUTYZI",
            },
            "outputs": {
                "answer": "This isn't covered in the video.",
                "evidence": "No transcript passage answers this question.",
            },
        },
        {
            "inputs": {
                "question": "What is microservices architecture?",
                "video_id": "SLHCfIUTYZI",
            },
            "outputs": {
                "answer": "Applications that are built as individual or siloed applications, each with their own individual data stores",
                "evidence": "[1:31] Applications that are built as individual or siloed applications, each with their own individual data stores",
            },
        },
        {
            "inputs": {
                "question": "What are pros of data streaming?",
                "video_id": "SLHCfIUTYZI",
            },
            "outputs": {
                "answer": "1. Real-time data. 2. Individual record events. 3. Mid-stream processing. 4. Scalable,",
                "evidence": "[4:24] Obviously, the biggest is that you're going to have access to near real-time data. You'll have access to all individual record events. You can run analysis or automatic mid-stream so you don't have to wait for that data to come through on a batch etl process, you can get at it right away. It's is also very scalable and fault tolerant as a result of that distributed architecture.",
            },
        },
        {
            "inputs": {
                "question": "Is data streaming hard to learn?",
                "video_id": "SLHCfIUTYZI",
            },
            "outputs": {
                "answer": "This is not covered in the video",
                "evidence": "No transcript passage answers this question.",
            },
        },
        # Pf-9pjJK1e0
        {
            "inputs": {
                "question": "What is horizontal scaling?",
                "video_id": "Pf-9pjJK1e0",
            },
            "outputs": {
                "answer": "horizontal scaling is when you add more instances instead of you just getting larger",
                "evidence": "[1:26] Horizontal scaling on the right side, you add more instances instead of you just getting larger and picking up the couch you invite some of your friends over and you all pick up the couch together.",
            },
        },
        {
            "inputs": {
                "question": "Explain horizontal scaling to me",
                "video_id": "Pf-9pjJK1e0",
            },
            "outputs": {
                "answer": "horizontal scaling is when you add more instances instead of you just getting larger",
                "evidence": "[1:26] Horizontal scaling on the right side, you add more instances instead of you just getting larger and picking up the couch you invite some of your friends over and you all pick up the couch together.",
            },
        },
        {
            "inputs": {
                "question": "Are relationable databases horizontaly scalable?",
                "video_id": "Pf-9pjJK1e0",
            },
            "outputs": {
                "answer": "No, they are vertically scalable.",
                "evidence": "[1:02] a relational database is also going to be vertically scalable",
            },
        },
        {
            "inputs": {
                "question": "What are different types of nosql databases?",
                "video_id": "Pf-9pjJK1e0",
            },
            "outputs": {
                "answer": "1. Key-value database. 2.column-oriented database, 3. a document database. 4. a graph database",
                "evidence": "[2:55] there's not just one type of nosql database, it's many different types and you can pull in many types of unstructured and semi-structured data. so we have a key-value database, a column-oriented database, a document database and a graph database.",
            },
        },
        {
            "inputs": {
                "question": "Are sql databases good for storing structured data?",
                "video_id": "Pf-9pjJK1e0",
            },
            "outputs": {
                "answer": "Yes, SQL databases are good for storing structured data. They are very organized, using tables with columns and rows, which allows for easily understood data integrity",
                "evidence": "[4:25] so for a sql database it's going to be very good at storing structure to data, has very easily understood data integrity a lot more",
            },
        },
        # ukzFI9rgwfU
        {
            "inputs": {
                "question": "What is machine learning?",
                "video_id": "ukzFI9rgwfU",
            },
            "outputs": {
                "answer": "Machine learning is training the machines to learn from the past data and do what humans can do and much faster",
                "evidence": "[0:00] Machines follow instructions given by humans but what if humans can train the machines to learn from the past data and do what humans can do and much faster.",
            },
        },
        {
            "inputs": {
                "question": "How does machines learn?",
                "video_id": "ukzFI9rgwfU",
            },
            "outputs": {
                "answer": "supervised learning, unsupervised learning, or reinforcement learning",
                "evidence": "[2:44] There are many ways in which the machine learns. It could be either supervised learning, unsupervised learning, or reinforcement learning.",
            },
        },
        {
            "inputs": {
                "question": "In which ways do machines learn?",
                "video_id": "ukzFI9rgwfU",
            },
            "outputs": {
                "answer": "Many ways: supervised learning, unsupervised learning, or reinforcement learning",
                "evidence": "[2:44] There are many ways in which the machine learns. It could be either supervised learning, unsupervised learning, or reinforcement learning.",
            },
        },
        {
            "inputs": {
                "question": "Does supervised learning use unlabeled data to train the model?",
                "video_id": "ukzFI9rgwfU",
            },
            "outputs": {
                "answer": "No, Supervised learning uses labeled data to train the model",
                "evidence": "[3:36] Supervised learning uses labeled data to train the model",
            },
        },
        {
            "inputs": {
                "question": "Is machine learning a subset of artificial intelligence?",
                "video_id": "SLHCfIUTYZI",
            },
            "outputs": {
                "answer": "This isn't covered in the video.",
                "evidence": "No transcript passage answers this question.",
            },
        },
        # 6A7Rbl_FKMU
        {
            "inputs": {
                "question": "Summarize the seven brain exercises",
                "video_id": "6A7Rbl_FKMU",
            },
            "outputs": {
                "answer": "1.Schulte Table. 2.Multi-Color Text. 3.Blindfolded Tasks. 4.Hand Coordination. 5.Non-Dominant Hand Tasks. 6.Brain Games. 7.Limiting technology dependence",
                "evidence": "",
            },
        },
        {
            "inputs": {
                "question": "Summarize the section 4:00 to 4:25",
                "video_id": "6A7Rbl_FKMU",
            },
            "outputs": {
                "answer": "Playing brain-challenging games like Sudoku, chess, riddles, and word puzzles can improve memory and decision-making. Choose games that stimulate your mind rather than addictive games like Candy Crush. You can also try free brain-training games on Lumosity",
                "evidence": "[4:00] exercise 6 brain games we often hear that video games are addictive but research shows that brain challenging games can improve decision-making and memory opt for games like Sudoku chess riddles or word scrambles that make you think rather than addictive games like Candy Crush websites like Lumosity offer a variety of free brain training games to keep you sharp",
            },
        },
        {
            "inputs": {
                "question": "Is machine learning a subset of artificial intelligence?",
                "video_id": "6A7Rbl_FKMU",
            },
            "outputs": {
                "answer": "This isn't covered in the video.",
                "evidence": "No transcript passage answers this question.",
            },
        },
        # EDb37y_MhRw
        {
            "inputs": {
                "question": "What makes agentic different from generative AI ",
                "video_id": "EDb37y_MhRw",
            },
            "outputs": {
                "answer": "They are proactive systems. Now, like generative AI, they often start with a user prompt, but that prompt is then used to pursue goals through a series of actions and an agentic system basically goes through a bit of a life cycle. So the way this works is it kind of first of all perceives it perceives its environment if you like and then once it's done that it can decide an action to take.",
                "evidence": "[1:31] Now, agentic AI systems, by contrast, those are not reactive. They are proactive systems. Now, like generative AI, they often start with a user prompt, but that prompt is then used to pursue goals through a series of actions and an agentic system basically goes through a bit of a life cycle. So the way this works is it kind of first of all perceives it perceives its environment if you like and then once it's done that it can decide an action to take.",
            },
        },
        {
            "inputs": {
                "question": "Explain multi-step processes to me?",
                "video_id": "EDb37y_MhRw",
            },
            "outputs": {
                "answer": "Multi-step processing refers to breaking down complex tasks into smaller, logical steps, similar to how humans approach difficult problems. For example, when planning a conference, an agent would first identify the requirements such as size, duration, and budget",
                "evidence": "[5:38] Multi-step processing refers to breaking down complex tasks into smaller, logical steps, similar to how humans approach difficult problems. For example, when planning a conference, an agent would first identify the requirements such as size, duration, and budget",
            },
        },
        {
            "inputs": {
                "question": "What is multi-step process?",
                "video_id": "EDb37y_MhRw",
            },
            "outputs": {
                "answer": "Multi-step processing refers to breaking down complex tasks into smaller, logical steps, similar to how humans approach difficult problems. For example, when planning a conference, an agent would first identify the requirements such as size, duration, and budget",
                "evidence": "[5:38] Multi-step processing refers to breaking down complex tasks into smaller, logical steps, similar to how humans approach difficult problems. For example, when planning a conference, an agent would first identify the requirements such as size, duration, and budget",
            },
        },
        {
            "inputs": {
                "question": "How does it use gen ai to generate an internal dialog?",
                "video_id": "EDb37y_MhRw",
            },
            "outputs": {
                "answer": "1.understand the conference requirements of the size, the duration, the budget, that sort of thing. 2.research available venues matching those parameters. 3. it might think well for those venues that meet those requirements I now need to check availability and so on",
                "evidence": "[5:57] So what it's going to do is it's going to use gen ai to generate an internal dialog. And that dialog might go something like this. It might say. First I need to understand the conference requirements of the size, the duration, the budget, that sort of thing. Then I should research available venues matching those parameters. Then it might think well for those venues that meet those requirements I now need to check availability and so on. It's effectively the agent really kind of talking to itself to explore the problem space before taking action. Gen AI is basically the cognitive engine driving an agent's decision-making. Now looking ahead, the most powerful AI systems probably won't be purely generative or purely agentic.",
            },
        },
        {
            "inputs": {
                "question": "What is common foundation between AI approaches?",
                "video_id": "EDb37y_MhRw",
            },
            "outputs": {
                "answer": "that common foundation is large language models or LLMs.",
                "evidence": "[2:27] And that common foundation is large language models or LLMs. LLMs serve as the backbone for chatbots and yeah there's actually other tools that are used for some of these other generative things, diffusion models typically for images and audio, but for chat bots we use LLMS and LLMs also provide the reasoning engine that powers agentic systems, but before we go any deeper into that let's talk about some real world applications and use cases.",
            },
        },
    ],
)