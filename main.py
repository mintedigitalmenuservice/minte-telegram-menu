import os
import staypresent

staypresent.run(
    "minte_restorant_bot.py",
    port=int(os.getenv("PORT", 8080))
)
