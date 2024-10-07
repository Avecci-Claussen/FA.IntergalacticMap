import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QPushButton,
    QListWidget, QHBoxLayout, QVBoxLayout, QWidget, QListWidgetItem, QMessageBox,
    QGraphicsTextItem, QGraphicsPixmapItem, QLabel
)
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor, QTransform, QImage
from PyQt5.QtCore import Qt, QRectF, QThread, pyqtSignal
import webbrowser
import requests
from PIL import Image
import io
class CustomScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent

    def mouseDoubleClickEvent(self, event):
        # Handle double-click on galaxy or planet text items and images
        item = self.itemAt(event.scenePos(), QTransform())

        if isinstance(item, QGraphicsTextItem) or isinstance(item, QGraphicsPixmapItem):
            item_type = item.data(Qt.UserRole)

            if item_type == "galaxy":
                galaxy_name = item.data(Qt.UserRole + 1)
                print(f"Double-clicked on galaxy: {galaxy_name}")
                self.parent_window.show_planets(galaxy_name)

            elif item_type == "planet":
                planet_name = item.data(Qt.UserRole + 1)
                print(f"Double-clicked on planet: {planet_name}")
                self.parent_window.show_aliens(planet_name)
        super().mouseDoubleClickEvent(event)

class ImageLoaderThread(QThread):
    finished = pyqtSignal(QPixmap)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self._is_running = True

    def run(self):
        if not self._is_running:
            return
        pixmap = ensure_proper_png(self.url)
        if pixmap:  # Only emit if pixmap is valid
            self.finished.emit(pixmap)
        else:
            fallback_pixmap = QPixmap(100, 100)
            fallback_pixmap.fill(Qt.gray)  # Placeholder if image loading fails
            self.finished.emit(fallback_pixmap)

    def terminate_thread(self):
        self._is_running = False  # Stop the thread
        self.quit()
        self.wait()




def ensure_proper_png(image_url):
  """
  Downloads an image from the URL and ensures it's in the correct format for display.
  """
  try:
      response = requests.get(image_url)
      if response.status_code == 200:
          image_data = response.content
          image = Image.open(io.BytesIO(image_data))
          
          # Convert image to RGB mode if it's not already
          if image.mode != 'RGB':
              image = image.convert('RGB')
          
          # Save the image as PNG in a bytes buffer
          buffer = io.BytesIO()
          image.save(buffer, format='PNG')
          buffer.seek(0)
          
          # Create QPixmap from the PNG data
          pixmap = QPixmap()
          pixmap.loadFromData(buffer.getvalue())
          
          if not pixmap.isNull():
              return pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
          else:
              print(f"Failed to create QPixmap from {image_url}")
      else:
          print(f"Failed to download image from {image_url}: {response.status_code}")
  except Exception as e:
      print(f"Error loading image from {image_url}: {e}")
  return None


class GalaxyMap(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_loader_threads = []  # To keep track of running threads

        # Set window properties
        self.setWindowTitle("Interactive Galaxy Map")
        self.showMaximized()  # Open in fullscreen mode

        # Create the central widget


        # Set up the QGraphicsView and scene


        # Initialize data (PLACEHOLDERS for galaxies, planets, and aliens)
        self.galaxies = {
            "Obscura": {"position": (333, 100), "planets": ["Nocturnis", "Nyxara"]},
            "Pyron": {"position": (900, 550), "planets": ["Ignis"]},
            "Crystallum": {"position": (600, 200), "planets": ["Xylox", "Glacionis"]},
            "Nebula Magna": {"position": (88, 300), "planets": ["Velarion"]},
            "Technara Nexus": {"position": (400, 350), "planets": ["Mecharis"]},
            "Spiralis Cluster": {"position": (900, 400), "planets": ["Fractalis"]},
            "Phantom Nebula": {"position": (200, 500), "planets": ["Spectralis"]},
            "Verdantis System": {"position": (400, 550), "planets": ["Floralis"]},
            "Astralis Rift": {"position": (70, 600), "planets": ["Lunaris", "Astralos"]},
            "Tenebris Expanse": {"position": (500, 500), "planets": ["Obscurium", "Subterra", "Silvorn"]},
            "Zephyros Cluster": {"position": (200, 750), "planets": ["Zephyros"]},
            "Braxil Galaxy": {"position": (700, 500), "planets": ["Braxil"]},
            "Aetheron Expanse": {"position": (800, 900), "planets": ["Aetheron"]},
        }

        self.planets = {
            "Nocturnis": {"position": (50, 300), "logo": "planets/Nocturnis.png", "aliens": [
                {
                    "name": "Umbrix",
                    "inscription_id": "9b6919ab76e89de9965d9e028e7a5af2525897b20b5052ed6720a8e98ad081dbi0",
                    "description": "🌙Meet Umbrix 🛸 \n\n The shadowy guardian from the planet Nocturnis (Obscura Galaxy). With the power to control shadows, absorb energy, and bend space, Umbrix maintains the balance between light and dark in its mysterious world."
                },
                {
                    "name": "Mokhtar",
                    "inscription_id": "8ac32e4a67e1dcf6a91e4a45985a2eee90e57ca5ba92bc101bf2c2c6d164075fi0",
                    "description": "🐪Meet Mokhtar🐪 \n\n A shadowy alien from Duskara, blends with the darkness of his sunless world. Born from shadows and sand, he moves unseen through the twilight, guarding his desolate planet. 🌑✨"
                },
                {
                    "name": "Okloni",
                    "inscription_id": "e118842606cd37bc4b8d9f5ea43100ce4c832ea864611a0eef8538151ba8cc0bi0",
                    "description": "🐪Meet Okloni \n\n With a form that merges with shadows and glowing blue eyes, Okloni embodies the mystery of the night. Draped in an ethereal cloak adorned with starlight, she protects the secrets of her dark world."
                },
            ]},
            "Nyxara": {"position": (700, 100), "logo": "planets/Nyxara.png", "aliens": [
                {
                    "name": "Nyxaris",
                    "inscription_id": "b7328d77c60bffbcbdef92f18abd4dcfa4d804a78ea22840561e837ec80d8c8ai0",
                    "description": "👽Meet Nyxaris👽 \n\n A semi-transparent, shadowy alien that creates illusions and portals through shadow manipulation."
                },
            ]},
            "Ignis": {"position": (787, 675), "logo": "planets/Ignis.png", "aliens": [
                {
                    "name": "Flamiris",
                    "inscription_id": "767a123afa54f4b55f165a2d9c9147ac8803248504fb6003fc6bb25eea4e792ai0",
                    "description": "🔥Meet Flamiris🔥 \n\n Flamiris, the molten guardian of planet Ignis! With a body of lava and flames, fiery cracks, and glowing eyes, Flamiris defends its volcanic world with fierce power."
                },
                {
                    "name": "Infernarus",
                    "inscription_id": "2341a21b0e6758e944c9d7c6ed94989c3b40a9982f537eab911a517db892cafdi0",
                    "description": "🌋Meet Infernarus🌋 \n\n The mighty guardian of Obsidion, wields the planet's molten magma with ease. Its obsidian body and glowing veins of magma make it a living volcano, protecting its world with volcanic eruptions and indestructible obsidian armor."
                },
            ]},
            "Xylox": {"position": (982, 50), "logo": "planets/Xylox.png", "aliens": [
                {
                    "name": "Crystarion",
                    "inscription_id": "0154a9a93909703ee7827e8a2c90f4cabfc00fdbc1124076a5927d96516ff902i0",
                    "description": "💎Meet Crystarion💎 \n\n The majestic crystalline guardian of planet Xylox (Crystallum Galaxy). With a body of sharp, refracting crystals and the power to manipulate light and energy, Crystarion ensures balance and harmony in its shimmering world."
                },
            ]},
            "Glacionis": {"position": (247, 200), "logo": "planets/Glacirian.png", "aliens": [
                {
                    "name": "Glacirian",
                    "inscription_id": "229c88b22f94db4709de31cacecdb1d28409da39630bc71b42c2e51551f6bf0fi0",
                    "description": "❄️ Meet Glacirian ❄️ \n\n The elegant guardian of Glacionis (Crystallum Galaxy). With a body made of shimmering ice and crystals, Glacirian controls frozen matter and protects its world with grace and power."
                },
            ]},
            "Velarion": {"position": (857, 200), "logo": "planets/Velarion.png", "aliens": [
                {
                    "name": "Nebulon",
                    "inscription_id": "1cb96919e53dcfd7b18855fd7e2d835940f84173383d39bdb1c5959e0e052c88i0",
                    "description": "🌌 Meet Nebulon 🌌 \n\n The ethereal guardian of Velarion (Nebula Magna Galaxy). Composed of swirling nebula gases, Nebulon manipulates cosmic clouds and creates stellar illusions to protect its world."
                },
            ]},
            "Mecharis": {"position": (450, 200), "logo": "planets/Mecharis.png", "aliens": [
                {
                    "name": "Mecharite",
                    "inscription_id": "8bac546ede73b4390393243336555294c6c4f71f1f5f79eaff00dae04f907d0fi0",
                    "description": "🦾Meet Mecharite🤖 \n\n A high-tech cyborg alien capable of interfacing with technology and evolving its cybernetic components."
                },
                {
                    "name": "Xyon",
                    "inscription_id": "93912b67d4f41b748e7724048219d88d05cfa088a3a730c7df5708aa7b796efci0",
                    "description": "🦾 Meet Xyon 🤖 \n\n Presenting Borg Xyon, a cybernetic being of unparalleled intelligence! With its half-machine, half-organic form, Xyon’s mind interfaces directly with advanced technology, navigating the digital cosmos in pursuit of perfection."
                },
            ]},
            "Fractalis": {"position": (600, 30), "logo": "planets/Fractalis.png", "aliens": [
                {
                    "name": "Fractalite",
                    "inscription_id": "da34d311c34d25642a10d79fad9d80cd28c4ff281dfffca34fd4955226add9eei0",
                    "description": "🌌Meet Elyon✨ \n\n A powerful Fractalite from the planet Fractalis, is the guardian of the galaxy’s fractal balance. With ever-shifting patterns of radiant energy, Elyon protects the cosmic harmony, ensuring the flow of fractal forces across dimensions."
                },
            ]},
            "Spectralis": {"position": (150, 671), "logo": "planets/Spectralis.png", "aliens": [
                {
                    "name": "Vaporous Phantasm",
                    "inscription_id": "5c60082835aaedee864f3eaaf06117fc730ee22928419612b35c7a9a1a7a2471i0",
                    "description": "👻Meet Olvari “The Glowing Phantasm”👻 \n\n A more defined, radiant entity, the Glowing Phantasm emits light from its ethereal form. It can project beams of light, create energy shields, and blend into the mist."
                },
            ]},
            "Floralis": {"position": (300, 500), "logo": "planets/Floralis.png", "aliens": [
                {
                    "name": "Floralith",
                    "inscription_id": "179ef7c1eefce332e6871133ca77c4bb74cc8a0de8a6c437bc675460961a26a5i0",
                    "description": "☘️🌿Meet Floralith 🍃 \n\n Guardian of the sacred flora on Floralis, stands tall with bioluminescent vines and rare, glowing flowers. It commands the planet’s flora, healing and protecting its vibrant ecosystem."
                },
                {
                    "name": "Lomira",
                    "inscription_id": "267494a7fa602b31c100f83976c13a46a25221b567f1747a9ed190b65f2d7ffai0",
                    "description": "💠Meet Lomira \n\n With her vibrant floral patterns and bioluminescent glow, she embodies the harmony of her home planet. Lomira harnesses the energy of light, creating mesmerizing displays that captivate all who encounter her."
                },
            ]},
            "Lunaris": {"position": (450, 840), "logo": "planets/Lunaris.png", "aliens": [
                {
                    "name": "Aurelis",
                    "inscription_id": "547117c20ec5f68201a234b4f00605390379d083f41f60168a221ef317c92264i0",
                    "description": "✨Meet Aurelis 🌟 \n\n The high-caste Lunarid from Lunaris, commands the power of light and lunar energy. With its crystalline body and the ability to phase between dimensions, it protects the sacred crystal lakes and floating islands of its world."
                },
            ]},
            "Obscurium": {"position": (500, 700), "logo": "planets/Obscurium.png", "aliens": [
                {
                    "name": "Nyxion",
                    "inscription_id": "74c3e659c41c51fc8508536b4e831865c3c2fe4658d5d67efbfea02b40953dd9i0",
                    "description": "🌌Meet Nyxion 👽 \n\n The shadowy guardian of Obscurium planet! Controls the dark matter and gravitational forces of its world. Born from pure darkness, it phases through shadows and distorts space to protect its home."
                },
            ]},
            "Astralos": {"position": (70, 600), "logo": "planets/Astralos.png", "aliens": [
                {
                    "name": "Zylar",
                    "inscription_id": "9415e862e56c2ecea3817dfb4df26f727fbf028e5147840b288342bb0c77e78ci0",
                    "description": "💠Meet Zylar💠 \n\n An ethereal alien from the planet Astralos, with a sleek, translucent form that shimmers with glowing blue and silver light patterns."
                },

            ]},
            "Subterra": {"position": (200, 720), "logo": "planets/Subterra.png", "aliens": [
                {
                    "name": "Lord Vextran",
                    "inscription_id": "75e93471d2ed9c7ac5b57f736fba7bd4ea006cd7d61b590e4bf1680adae1ff54i0",
                    "description": "⚔️ Meet Lord Vextran \n\n The malevolent ruler of Subterra! Cloaked in shadows and adorned with glowing patterns, he commands dark powers that threaten the balance of his underground world."
                },
                {
                    "name": "Vorpax",
                    "inscription_id": "674fb7930dbb7eeb9de09ca12a589ecd3dc5a31242f5961574e03a13178d7e0fi0",
                    "description": "⚔️ Meet Vorpax  \n\n A shadowy alien from the planet Subterra, where darkness has taken over. Vorpax embodies pure shadow, with jagged, shifting features and tendrils of dark energy."
                },
                {
                    "name": "Drexon",
                    "inscription_id": "758e6055277111694a7829a0acc447974bb9b0b29522d23f6405a227a127fb37i0",
                    "description": "⚔️ Meet Drexon  \n\n The loyal Warrior of Lord Vextran! With his dark metallic skin and glowing fractal patterns, he embodies the dangers of his treacherous planet."
                },
            ]},
            "Silvorn": {"position": (900, 750), "logo": "planets/Silvorn.png", "aliens": [
                {
                    "name": "Sovrin",
                    "inscription_id": "d5b19e0976b0946e4f82af7fea9b06812c8d270d6dca1279cb9f43a9dd3df415i0",
                    "description": "🌌 Meet Sovrin, the elite guardian of Silvorn!🛡️ With his dark metallic skin and glowing fractal patterns, he embodies strength and authority."
                },
                {
                    "name": "Zamora",
                    "inscription_id": "6ae027265801fecc41ff030b4419c816aac64830f977ddeea42d121beed1331ai0",
                    "description": "🌌 Introducing Zamora, the resilient survivor of Silvorn!🛡️ With her dark metallic skin and glowing patterns, she navigates the dangers of her home with agility and cunning."
                },
            ]},
            "Zephyros": {"position": (650, 780), "logo": "planets/Zephyros.png", "aliens": [
                {
                    "name": "Juvessa",
                    "inscription_id": "fc8fc6d136ca4a4e0b1df520f04300e05591f5956e2ffd6227b70148c03038fdi0",
                    "description": "💠Meet Juvessa \n\n The swift alien from the high-speed planet Zephyros. Adorned with glowing, intricate patterns that pulse with vibrant blue and silver light."
                },
                {
                    "name": "Skrillox",
                    "inscription_id": "e8c81f32ce47b3391796c62af4562f7c05412da8538be684032c0bafa23fba66i0",
                    "description": "Meet Skrillox \n\n The windborne alien from the planet Zephyros. With sleek, aerodynamic features and glowing silver and gold patterns, Skrillox rides the powerful winds of its world."
                },
            ]},
            "Braxil": {"position": (700, 800), "logo": "planets/Braxil.png", "aliens": [
                {
                    "name": "Yarvok",
                    "inscription_id": "27557dfe62cab1b0693cb4fb16a66df8dcc8e5b667fc18317d9fd968b9864a9ci0",
                    "description": "💠Meet Yarvok \n\n A towering, rock-like warrior from Braxil. Harnessing the planet’s raw energy, he defends his world with unmatched strength."
                },
                {
                    "name": "Vilmor",
                    "inscription_id": "81295c2c2478f08ac2f9e63a72783a830e56e3de62ab5c843bfd1e629ab75b9ai0",
                    "description": "💠Meet Vilmor💠 \n\n Vilmor embodies the peaceful, mystical energy of Astralos, using its power to manipulate light and cosmic forces to maintain harmony."
                },
            ]},
            "Aetheron": {"position": (750, 820), "logo": "planets/Aetheron.png", "aliens": [
                {
                    "name": "Aeloria",
                    "inscription_id": "c046c824dd1b2b83c4d426561458cc6c9ec6fbab142ec8eaf6576431a6691113i0",
                    "description": "🌌 Meet Aeloria \n\n The enchanting guardian of Aetheron! With her sleek, elongated form and glowing patterns, she embodies the magic of her floating world."
                },
            ]},
        }


        # Add galaxy name to each planet for back navigation
        for planet, info in self.planets.items():
            info["galaxy"] = next((galaxy for galaxy, g_info in self.galaxies.items() if planet in g_info["planets"]), None)

        # Create a stack to keep track of navigation history
        self.navigation_stack = []

        # Set up the main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Set up the sidebar with a vertical layout
        self.sidebar_widget = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.main_layout.addWidget(self.sidebar_widget, stretch=1)  # 20%

        # Set up the Back button inside the sidebar
        self.back_button = QPushButton("Back")
        self.back_button.setObjectName("back_button")  # Assign object name for specific styling
        self.back_button.setFixedHeight(40)
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setVisible(False)
        self.sidebar_layout.addWidget(self.back_button)

        # Set up the QListWidget for the sidebar
        self.sidebar = QListWidget()
        self.sidebar.itemClicked.connect(self.handle_sidebar_click)
        self.sidebar.itemDoubleClicked.connect(self.handle_sidebar_double_click)  # Connect double-click
        self.sidebar_layout.addWidget(self.sidebar, stretch=1)

        # Add a spacer to separate the list and the details panel
        self.sidebar_layout.addSpacing(10)

        # Create the details panel widget
        self.alien_details_widget = QWidget()
        self.alien_details_layout = QVBoxLayout(self.alien_details_widget)

        # Alien Logo
        self.alien_logo_label = QLabel()
        self.alien_logo_label.setAlignment(Qt.AlignCenter)
        self.alien_logo_label.setFixedSize(500, 500)  # Adjust size as needed
        self.alien_details_layout.addWidget(self.alien_logo_label)

        # Alien Description
        self.alien_description_label = QLabel("Description goes here.")
        self.alien_description_label.setWordWrap(True)
        self.alien_description_label.setStyleSheet("color: #ffffff;")
        self.alien_details_layout.addWidget(self.alien_description_label)

        # Initially hide the details panel
        self.alien_details_widget.setVisible(False)

        # Add the details panel to the sidebar layout
        self.sidebar_layout.addWidget(self.alien_details_widget)

        self.scene = CustomScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.view, stretch=4)  

        # Load and display the background image (galaxy map)
        self.background_pixmap = QPixmap('back.jpg').scaled(1600, 900, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        if self.background_pixmap.isNull():
            QMessageBox.warning(self, "Image Load Error", "Background image 'back.jpg' not found or cannot be loaded.")
        self.background_item = QGraphicsPixmapItem(self.background_pixmap)
        self.background_item.setZValue(-1)  # Ensure background is behind other items
        self.scene.addItem(self.background_item)
        self.scene.setSceneRect(0, 0, self.background_pixmap.width(), self.background_pixmap.height())

        # Show galaxies initially
        self.show_galaxies()

    def show_galaxies(self):
        self.clear_sidebar()
        # Clear the scene except the background
        self.clear_scene(exclude_items=(self.background_item,))
        # Populate sidebar with galaxies
        for galaxy_name in self.galaxies.keys():
            item = QListWidgetItem(galaxy_name)
            item.setData(Qt.UserRole, {"type": "galaxy", "name": galaxy_name})
            self.sidebar.addItem(item)

        # Add galaxies to the scene
        for galaxy_name, galaxy_info in self.galaxies.items():
            x, y = galaxy_info["position"]
            print(f"Adding galaxy '{galaxy_name}' at position ({x}, {y})")
            galaxy_text = QGraphicsTextItem(galaxy_name)
            galaxy_text.setFont(QFont("Helvetica", 16))
            galaxy_text.setDefaultTextColor(Qt.white)
            galaxy_text.setPos(x, y)
            galaxy_text.setData(Qt.UserRole, "galaxy")
            galaxy_text.setData(Qt.UserRole + 1, galaxy_name)
            self.scene.addItem(galaxy_text)

            
    def show_planets(self, galaxy_name):
      # Push current view to navigation stack
      self.navigation_stack.append(lambda: self.show_galaxies())
      
      self.clear_sidebar()
      self.clear_scene(exclude_items=(self.background_item,))

      for planet_name in self.galaxies[galaxy_name]["planets"]:
          item = QListWidgetItem(planet_name)
          item.setData(Qt.UserRole, {"type": "planet", "name": planet_name, "galaxy": galaxy_name})
          self.sidebar.addItem(item)

      self.back_button.setVisible(True)

      for planet_name in self.galaxies[galaxy_name]["planets"]:
          planet_info = self.planets.get(planet_name, {})
          x, y = planet_info["position"]

          planet_text = QGraphicsTextItem(planet_name)
          planet_text.setFont(QFont("Helvetica", 14))
          planet_text.setDefaultTextColor(Qt.white)
          planet_text.setPos(x, y)
          planet_text.setData(Qt.UserRole, "planet")
          planet_text.setData(Qt.UserRole + 1, planet_name)
          self.scene.addItem(planet_text)

          logo_path = planet_info.get("logo")
          if logo_path:
              pixmap = QPixmap(logo_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
              if pixmap.isNull():
                  print(f"Warning: Planet logo '{logo_path}' not found or cannot be loaded.")
              else:
                  logo_item = QGraphicsPixmapItem(pixmap)
                  logo_item.setPos(x + 20, y + 20)
                  logo_item.setZValue(-0.5)
                  logo_item.setData(Qt.UserRole, "planet")
                  logo_item.setData(Qt.UserRole + 1, planet_name)
                  self.scene.addItem(logo_item)

    def show_aliens(self, planet_name):
      # Push current view to navigation stack
      galaxy_name = self.planets[planet_name]["galaxy"]
      self.navigation_stack.append(lambda: self.show_planets(galaxy_name))
      
      self.clear_sidebar()
      for alien in self.planets[planet_name]["aliens"]:
          item = QListWidgetItem(self.sidebar)
          widget = QWidget()
          layout = QHBoxLayout(widget)
          
          # Alien logo
          logo_label = QLabel()
          logo_url = f"https://fractal-static.unisat.io/content/{alien['inscription_id']}"
          loader = ImageLoaderThread(logo_url)
          loader.finished.connect(lambda pixmap, label=logo_label: label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
          loader.start()
          self.image_loader_threads.append(loader)
          layout.addWidget(logo_label)
          
          # Alien name and inscription ID
          text_label = QLabel(f"{alien['name']} - {alien['inscription_id']}")
          layout.addWidget(text_label)
          
          item.setSizeHint(widget.sizeHint())
          self.sidebar.setItemWidget(item, widget)
          item.setData(Qt.UserRole, {"type": "alien", "inscription_id": alien["inscription_id"]})

      self.back_button.setVisible(True)

      # Clear existing items from scene except background
      self.clear_scene(exclude_items=(self.background_item,))

      # Optionally, display planet name and logo in the main view when viewing aliens
      planet_info = self.planets.get(planet_name, {})
      if planet_info:
          x, y = planet_info["position"]
          planet_text = QGraphicsTextItem(planet_name)
          planet_text.setFont(QFont("Helvetica", 14))
          planet_text.setDefaultTextColor(Qt.white)
          planet_text.setPos(x, y)
          planet_text.setData(Qt.UserRole, "planet")
          planet_text.setData(Qt.UserRole + 1, planet_name)
          self.scene.addItem(planet_text)

          logo_path = planet_info.get("logo")
          if logo_path:
              planet_logo = QPixmap(logo_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
              if not planet_logo.isNull():
                  logo_item = QGraphicsPixmapItem(planet_logo)
                  logo_item.setPos(x + 20, y + 20)
                  logo_item.setZValue(-0.5)
                  logo_item.setData(Qt.UserRole, "planet")
                  logo_item.setData(Qt.UserRole + 1, planet_name)
                  self.scene.addItem(logo_item)


    def handle_sidebar_click(self, item):
        data = item.data(Qt.UserRole)
        if data:
            if data["type"] == "galaxy":
                print(f"Sidebar: Selecting galaxy '{data['name']}'")
                self.show_planets(data["name"])
                # Hide the alien details panel if visible
                self.alien_details_widget.setVisible(False)
            elif data["type"] == "planet":
                print(f"Sidebar: Selecting planet '{data['name']}'")
                self.show_aliens(data["name"])
                # Hide the alien details panel if visible
                self.alien_details_widget.setVisible(False)
            elif data["type"] == "alien":
                print(f"Sidebar: Selecting alien '{item.text()}'")
                # Populate and show the details panel
                self.display_alien_details(data["inscription_id"])

    def handle_sidebar_double_click(self, item):
        data = item.data(Qt.UserRole)
        if data and data["type"] == "alien":
            inscription_id = data["inscription_id"]
            if inscription_id:  # Ensure there is an inscription_id
                print(f"Sidebar: Double-clicking alien with inscription_id '{inscription_id}'")
                self.open_marketplace(inscription_id)
            else:
                QMessageBox.information(self, "No Inscription ID", "This alien does not have an inscription ID.")
    def go_back(self):
      if self.navigation_stack:
          previous_action = self.navigation_stack.pop()
          previous_action()
      self.back_button.setVisible(bool(self.navigation_stack))
      self.alien_details_widget.setVisible(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_size = self.view.size()
        self.background_pixmap = QPixmap('back.jpg').scaled(new_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        if self.background_pixmap.isNull():
            pass  # Already handled in init
        self.background_item.setPixmap(self.background_pixmap)
        self.scene.setSceneRect(0, 0, self.background_pixmap.width(), self.background_pixmap.height())
        print("Resized background pixmap")
    def open_marketplace(self, inscription_id):
        url = f"https://fractal.unisat.io/inscription/{inscription_id}"
        print(f"Opening URL: {url}")
        webbrowser.open(url)

    def clear_sidebar(self):
        self.sidebar.clear()
        # Also hide the alien details panel
        self.alien_details_widget.setVisible(False)

    def clear_scene(self, exclude_items=()):
        for item in self.scene.items():
            if item in exclude_items:
                continue
            if isinstance(item, QGraphicsPixmapItem):
                if item != self.background_item:
                    self.scene.removeItem(item)
            elif isinstance(item, QGraphicsTextItem):
                self.scene.removeItem(item)


    def display_alien_details(self, inscription_id):
        # Find the alien based on inscription_id
        alien = None
        for planet_info in self.planets.values():
            for a in planet_info.get("aliens", []):
                if a["inscription_id"] == inscription_id:
                    alien = a
                    break
            if alien:
                break
    
        if alien:
            image_url = f"https://fractal-static.unisat.io/content/{inscription_id}"
            loader = ImageLoaderThread(image_url)
            loader.finished.connect(self.set_alien_image)
            loader.start()

            self.image_loader_threads.append(loader)  # Keep track of threads

            description = alien.get("description", "No description available.")
            self.alien_description_label.setText(description)

            # Show the details panel
            self.alien_details_widget.setVisible(True)
        else:
            self.alien_details_widget.setVisible(False)
            QMessageBox.warning(self, "Alien Not Found", "The selected alien could not be found.")

    
    def set_alien_image(self, pixmap):
        if pixmap:
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.alien_logo_label.setPixmap(scaled_pixmap)

        else:
            self.alien_logo_label.setText("Failed to load image.")

    def closeEvent(self, event):
        # When the window is closed, ensure all threads are terminated
        for thread in self.image_loader_threads:
            thread.terminate_thread()
        event.accept()


# Main function to run the PyQt5 application
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Define a simple dark stylesheet
    dark_stylesheet = """
        /* General QWidget background and text color */
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }

        /* QPushButton specific styling */
        QPushButton {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 5px;
        }

        QPushButton:hover {
            background-color: #4c4c4c;
        }

        /* QListWidget specific styling */
        QListWidget {
            background-color: #3c3c3c;
            border: 1px solid #555555;
        }

        QListWidget::item:selected {
            background-color: #555555;
        }

        /* QGraphicsView background */
        QGraphicsView {
            background-color: #1e1e1e;
        }

        /* Back Button styling */
        QPushButton#back_button {
            background-color: #3c3c3c;
            color: #ffffff;
        }
    """

    # Apply the dark stylesheet
    app.setStyleSheet(dark_stylesheet)

    galaxy_map = GalaxyMap()  # Instance of GalaxyMap
    galaxy_map.show()
    sys.exit(app.exec_())