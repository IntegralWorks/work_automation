import matplotlib
import matplotlib.pyplot as plt
import sys
import mss #screenshot library
import mss.tools
from PIL import Image
import io

with mss.mss() as sct:
    # Get information of monitor n
    monitor_number = int(sys.argv[1])
    mon = sct.monitors[monitor_number]

    # The screen part to capture
    monitor = {
        "top": mon["top"] + int(sys.argv[2]),  # px from the top
        "left": mon["left"] + int(sys.argv[3]),  # px from the left
        "width": int(sys.argv[4]),
        "height": int(sys.argv[5]),
        "mon": monitor_number,
    }
    
    def screenshot(label=sys.argv[6]):
        sct_img = sct.grab(monitor)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output='tmp.png')
        plt.imshow(Image.open('tmp.png'))
        plt.axis('off')
        plt.text(378, 30, label, size=10, rotation=0,
         ha="center", va="center", c='white',
         bbox=dict(boxstyle="round", fc='black', ec='grey',
                   # ec=(1., 0.5, 0.5),
                   # fc=(1., 0.8, 0.8),
                   )
         )
        pic = io.BytesIO()
        plt.savefig(pic, pad_inches = 0, bbox_inches = 'tight', format='png', dpi=400)
        plt.show()
        plt.close()

    screenshot()
