
from AISimuToolKit.exp.experiment import Experiment
from AISimuToolKit.exp.agents.agent import Agent
import gradio as gr
import cv2
import base64
from typing import Dict, List, Tuple
import itertools



def cover_img(background, img, place: Tuple[int, int]):
    """
    Overlays the specified image to the specified position of the background image.
    :param background: background image
    :param img: the specified image
    :param place: the top-left coordinate of the target location
    """
    back_h, back_w, _ = background.shape
    height, width, _ = img.shape
    for i, j in itertools.product(range(height), range(width)):
        if img[i, j, 3]:
            background[place[0] + i, place[1] + j] = img[i, j, :3]
            
            
def reset_exp() -> Experiment:   
    Agent.idx=0         
    exp = Experiment.load(config="/home/renmengjie2021/projects/AISimulation/AISimuToolKit/test/files4test/leaderless_discuss/exp_leaderless_discuss.json",
                          model_config="/home/renmengjie2021/projects/AISimulation/AISimuToolKit/test/files4test/leaderless_discuss/model.yaml",
                          output_dir="/home/renmengjie2021/projects/AISimulation/AISimuToolKit/experiments")
    exp.inject_background(
        message='is at school interviewing for the Olympics. This is a leaderless panel. The topic of discussion was "Minority language volunteers take half an hour to get to the site. As the only volunteer on site, now how will you inform foreigners of minority language that they must wear masks before entering the site". Ask you to discuss a solution')
    return exp
            

class UI:
    """
    the UI of frontend
    """

    def __init__(self):
        """
        init a UI.
        default number of students is 0
        """
        self.messages = []
        self.exp = None
        
        self.autoplay = False
        self.image_now = None
        self.text_now = None

    def get_avatar(self, idx):
        img = cv2.imread(f"/home/renmengjie2021/projects/AISimulation/AISimuToolKit/test/files4test/leaderless_discuss/imgs/{idx}.png", cv2.IMREAD_UNCHANGED)
        base64_str = cv2.imencode(".png", img)[1].tostring()
        return "data:image/png;base64," + base64.b64encode(base64_str).decode("utf-8")

    def stop_autoplay(self):
        self.autoplay = False
        return (
            gr.Button.update(interactive=False),
            gr.Button.update(interactive=False),
            gr.Button.update(interactive=False),
        )

    def start_autoplay(self):
        self.autoplay = True
        yield self.image_now, self.text_now, gr.Button.update(
            interactive=False
        ), gr.Button.update(interactive=True), gr.Button.update(interactive=False)
        while self.autoplay:
            outputs = self.gen_output()
            self.image_now, self.text_now = outputs
            yield *outputs, gr.Button.update(
                interactive=not self.autoplay
            ), gr.Button.update(interactive=self.autoplay), gr.Button.update(
                interactive=not self.autoplay
            )

    def delay_gen_output(self):
        yield self.image_now, self.text_now, gr.Button.update(
            interactive=False
        ), gr.Button.update(interactive=False)
        outputs = self.gen_output()
        self.image_now, self.text_now = outputs
        yield self.image_now, self.text_now, gr.Button.update(
            interactive=True
        ), gr.Button.update(interactive=True)

    def delay_reset(self):
        self.autoplay = False
        self.image_now, self.text_now = self.reset()
        return (
            self.image_now,
            self.text_now,
            gr.Button.update(interactive=True),
            gr.Button.update(interactive=False),
            gr.Button.update(interactive=True),
        )

    def reset(self):
        """
        tell backend the new number of students and generate new empty image
        :param stu_num:
        :return: [empty image, empty message]
        """
        self.exp = reset_exp()
        background = cv2.imread("/home/renmengjie2021/projects/AISimulation/AISimuToolKit/test/files4test/leaderless_discuss/imgs/background.png")
        self.messages = []
        return [cv2.cvtColor(background, cv2.COLOR_BGR2RGB), ""]

    def gen_img(self, datas: List[Dict]):
        """
        generate new image with sender rank
        :param data:
        :return: the new image
        """
        img = cv2.imread("/home/renmengjie2021/projects/AISimulation/AISimuToolKit/test/files4test/leaderless_discuss/imgs/speaking.png", cv2.IMREAD_UNCHANGED)
        background = cv2.imread("/home/renmengjie2021/projects/AISimulation/AISimuToolKit/test/files4test/leaderless_discuss/imgs/background.png")
        
        for data in datas:
            if data["agent"]==1:
                cover_img(background, img, (10, 30))
            elif data["agent"]==2:
                cover_img(background, img, (10, 55))
            elif data["agent"]==3:
                cover_img(background, img, (40, 30))
            elif data["agent"]==4:
                cover_img(background, img, (40, 55))
        return cv2.cvtColor(background, cv2.COLOR_BGR2RGB)


    def gen_output(self):
        """
        generate new image and message of next step
        :return: [new image, new message]
        """
        datas = self.exp.scheduler.run()
        self.messages.extend(datas)
        message = ""
        for data in self.messages.reverse():
            agent, msg = data["agent"], data["msg"]
            avatar = self.get_avatar((agent - 1) % 4 + 1)
            message = (
                message +
                f'<div style="display: flex; align-items: center; margin-bottom: 10px;overflow:auto;">'
                f'<img src="{avatar}" style="width: 10%; height: 10%; border-radius: 25px; margin-right: 10px;">'
                f'<div style="background-color: gray; color: white; padding: 10px; border-radius: 10px; max-width: 90%;font-size: 20px;">'
                f"{msg}"
                f"</div></div>"
            )
        message = '<div style="height:600px;overflow:auto;">' + message + "</div>"
        return [self.gen_img(datas), message]

    def launch(self):
        """
        start a frontend
        """
        with gr.Blocks() as demo:
            with gr.Row():
                with gr.Column(width=0.3, height=0.3):
                    image_output = gr.Image()
                    with gr.Row():
                        reset_btn = gr.Button("Reset")
                        # next_btn = gr.Button("Next", variant="primary")
                        next_btn = gr.Button("Next")
                        stop_autoplay_btn = gr.Button(
                            "Stop Autoplay", interactive=False
                        )
                        start_autoplay_btn = gr.Button("Start Autoplay")
                # text_output = gr.Textbox()
                text_output = gr.HTML()
                # text_output = gr.HTML(self.reset()[1])

            # Given a botton to provide student numbers and their inf.
            # stu_num = gr.Number(label="Student Number", precision=0)
            # stu_num = self.stu_num

            # next_btn.click(fn=self.gen_output, inputs=None, outputs=[image_output, text_output], show_progress=False)
            next_btn.click(
                fn=self.delay_gen_output,
                inputs=None,
                outputs=[image_output, text_output, next_btn, start_autoplay_btn],
                show_progress=False,
            )

            # [To-Do] Add botton: re-start (load different people and env)
            # reset_btn.click(fn=self.reset, inputs=stu_num, outputs=[image_output, text_output], show_progress=False)
            # reset_btn.click(fn=self.reset, inputs=None, outputs=[image_output, text_output], show_progress=False)
            reset_btn.click(
                fn=self.delay_reset,
                inputs=None,
                outputs=[
                    image_output,
                    text_output,
                    next_btn,
                    stop_autoplay_btn,
                    start_autoplay_btn,
                ],
                show_progress=False,
            )

            stop_autoplay_btn.click(
                fn=self.stop_autoplay,
                inputs=None,
                outputs=[next_btn, stop_autoplay_btn, start_autoplay_btn],
                show_progress=False,
            )
            start_autoplay_btn.click(
                fn=self.start_autoplay,
                inputs=None,
                outputs=[
                    image_output,
                    text_output,
                    next_btn,
                    stop_autoplay_btn,
                    start_autoplay_btn,
                ],
                show_progress=False,
            )

        demo.queue(concurrency_count=5, max_size=20).launch()
        # demo.launch()



def main():
    ui = UI()
    ui.launch()


if __name__ == '__main__':
    main()
