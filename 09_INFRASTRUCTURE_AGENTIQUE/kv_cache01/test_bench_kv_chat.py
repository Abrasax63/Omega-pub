import unittest
import bench_kv
import bench_kv_chat as chat

class ChatFrozenTests(unittest.TestCase):
    def test_distinct_new_additions(self):
        self.assertEqual(len(set(chat.CASES[:-1])),6)
        self.assertEqual(chat.CASES[0][1:],chat.CASES[-1][1:])
    def test_reference_additions(self):
        self.assertEqual([(x[2]+x[3])%x[1] for x in chat.CASES],[5,7,7,9,9,8,5])
    def test_chat_template_wrapper(self):
        p=chat.render_qwen_chat(chat.CASES[0])
        self.assertTrue(p.startswith("<|im_start|>system\n"))
        self.assertTrue(p.endswith("<|im_start|>assistant\n"))
        self.assertIn("Calcule exactement 2 + 3",p)
    def test_only_last_question_changes(self):
        a=chat.render_qwen_chat(chat.CASES[0]);b=chat.render_qwen_chat(chat.CASES[1])
        before=a.split("<|im_end|>\n<|im_start|>user\n")[0]
        before2=b.split("<|im_end|>\n<|im_start|>user\n")[0]
        self.assertEqual(before,before2)
    def test_cache_switch_does_not_change_prompt(self):
        saved=bench_kv.prompt_for
        try:
            bench_kv.prompt_for=chat.render_qwen_chat
            a=bench_kv.request_for(chat.CASES[0],False)
            b=bench_kv.request_for(chat.CASES[0],True)
            self.assertEqual(a["prompt"],b["prompt"])
            self.assertEqual({k:v for k,v in a.items() if k!="cache_prompt"},
                             {k:v for k,v in b.items() if k!="cache_prompt"})
        finally:bench_kv.prompt_for=saved

if __name__=="__main__":unittest.main()
