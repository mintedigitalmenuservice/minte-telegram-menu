import os
import staypresent

staypresent.run(
    "owner_minte_restorant_bot.py",
    port=int(os.getenv("PORT", 8080))
)
