# DocVeil vs GPT - Test Comparison

December 18, 2025

## Summary

So I ran the same PDF through both DocVeil (using Ollama locally) and GPT-4 to see which one gives better summaries. Used the exact same prompt for both. The results were pretty surprising.

**Bottom line: DocVeil absolutely crushed it.** Not even close.

---

## Test Setup

- Document: AI_ML_DL_LangChain_LangGraph.pdf (5 pages, technical content)
- Same prompt given to both systems (asked for detailed numbered summaries)
- DocVeil running Ollama with the LangGraph workflow
- GPT-4 via their web interface

---

## What I Got

**DocVeil:** 52 detailed points spread across all 5 pages
**GPT:** 13 points total, everything mashed together

Yeah, that's a 4x difference right there. But it's not just about the numbers.

### Example - Reinforcement Learning

Here's how they each handled the same concept:

**DocVeil:**

```
(4) Reinforcement learning is a paradigm where an agent learns by interacting with
    an environment and receiving feedback in the form of rewards or penalties. Over
    time, the agent learns strategies that maximize cumulative reward, making it
    commonly used in robotics, game playing, and control systems.
```

**GPT:**

```
(7) ML techniques are commonly divided into supervised learning, unsupervised
    learning, and reinforcement learning, each addressing different types of data
    and learning objectives such as prediction, pattern discovery, or reward-based
    decision-making.
```

DocVeil gives you a full explanation you can actually understand. GPT just mentions it in passing with two other things. Not very helpful if you're trying to learn.

---

## The Differences

### Structure

DocVeil breaks things down page by page:

- Page 1: AI (10 points)
- Page 2: ML (12 points)
- Page 3: Deep Learning (10 points)
- Page 4: LangChain (10 points)
- Page 5: LangGraph (10 points)

GPT just dumps 13 points in one list. No page separation, everything mixed together.

### Detail Level

DocVeil points average 40-60 words each. Complete sentences, proper explanations.

GPT points are like 15-25 words. More like bullet points than actual summaries.

Total word count:

- DocVeil: ~2,500 words
- GPT: ~450 words

### Quality

DocVeil summaries actually teach you something. Each point has enough context that you can understand it without reading the original.

GPT summaries are more like... reminders? If you already know the topic, they're fine. If you're trying to learn, not so much.

---

## What DocVeil Does Better

**Covers advanced topics:**
DocVeil mentions things like SHAP values, interpretability methods, data bias concerns, future research directions. GPT skips all that.

**Better organization:**
The page-by-page structure makes it way easier to navigate. GPT's flat list means you have to read everything to find what you want.

**Self-contained points:**
Each DocVeil point makes sense on its own. GPT points often reference other points or assume you know the context.

**Reads naturally:**
DocVeil uses complete sentences that flow well. Feels like reading an article. GPT is more choppy, bullet-point style.

---

## When You'd Use Each

### DocVeil is better for:

- Actually learning from the summary
- Research papers or technical docs
- When you need comprehensive coverage
- Building documentation or notes
- Sharing knowledge with your team

### GPT might be better for:

- Super quick scanning (under 1 minute)
- Just checking if a doc is relevant
- High-level topic overview

Honestly though, even for quick scans, I'd probably still use DocVeil. It's not that much longer to read and you actually get useful info.

---

## Numbers

Quick comparison:

|                 | DocVeil | GPT-4    |
| --------------- | ------- | -------- |
| Total points    | 52      | 13       |
| Words per point | 40-60   | 15-25    |
| Total words     | ~2,500  | ~450     |
| Page separation | Yes     | No       |
| Detail ratio    | 5:1     | baseline |

---

## Technical Notes

The DocVeil workflow uses LangGraph for stateful processing, which lets it:

- Process pages in parallel (fast)
- Refine summaries sequentially (quality)
- Maintain context across pages
- Keep everything organized

Running locally on Ollama means no API costs and data stays private..

---

## The Prompt (Same for Both)

Just to be clear, both systems got the exact same instructions:

```
You are a summarizer who can generate a detailed summary of {page_content}

Format your summary like this:
**Brief Topic/Heading** (describing what this page is about)

(1) First key point
(2) Second key point
(3) Third key point
(4) Fourth key point
... (continue with as many points as needed for a comprehensive summary)

IMPORTANT:
- Start with a brief heading in bold (**heading**) that captures the main topic
- Then provide numbered points (1), (2), (3), (4), (5), etc. - as many as needed
- Provide a DETAILED summary - aim for 7-10 points or more for comprehensive content
- Do not limit yourself to just 3 points - the examples above are not a maximum
- Do not use additional asterisks in the points themselves
```

So yeah, GPT had the same instructions asking for 7-10+ detailed points. It just... didn't do it.

---

## Conclusion

For detailed PDF summaries, DocVeil wins hands down. It's not a small difference - it's 5x more information, better organized, and actually useful for learning.

Kind of impressive that a local open-source model beats GPT-4 this badly. The LangGraph workflow definitely makes a difference.

**Test files:**  
DocVeil output: `summaries_output/f985a552-8d0b-4235-ace1-d9344fe5907a_summary_20251218_140905.txt`
