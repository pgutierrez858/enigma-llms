dataset = [
    {
        "name": "Apollo in the Forge of Vulcan",
        "description": "Diego Velázquez’s painting 'Apollo in the Forge of Vulcan' (c. 1630) depicts the Roman god "
                       "Vulcan at work in his forge, surrounded by assistants hammering metal in the intense heat. "
                       "The muscular Vulcan, engaged in forging, represents both creation and destruction. Velázquez "
                       "masterfully contrasts the warm glow of fire with cooler tones, creating a dramatic atmosphere "
                       "that blends mythology with naturalism. The painting humanizes Vulcan, portraying him as a "
                       "laborer rather than an idealized deity, making it an allegory of craftsmanship, creativity, "
                       "and transformation. Through his use of light and shadow, Velázquez enhances the realism and "
                       "depth of the scene, showcasing his technical mastery."
    },
    {
        "name": "Las Hilanderas",
        "description": "Diego Velázquez’s 'The Spinners' (c. 1657), also known as 'The Fable of Arachne,"
                       "' reinterprets the Greek myth of Arachne, a mortal weaver who dared to challenge Athena. "
                       "Instead of a direct depiction of the myth, Velázquez presents a busy weaving workshop, "
                       "where a young woman, likely Arachne, works on an intricate tapestry. In the background, "
                       "a woven scene alludes to Athena’s intervention and Arachne’s eventual transformation into a "
                       "spider. The painting merges realism with mythology, emphasizing the artistry of weaving and "
                       "the fine line between skill and hubris. With his signature mastery of light, texture, "
                       "and composition, Velázquez captures both everyday labor and the deeper themes of artistic "
                       "competition and divine justice."
    },
    {
        "name": "Judith at the Banquet of Holofernes",
        "description": "Rembrandt’s 'Judith at the Banquet of Holofernes' (1630s) offers a psychological and intimate "
                       "portrayal of the biblical heroine Judith, who seduces and beheads the Assyrian general "
                       "Holofernes to save her people. Unlike traditional dramatic depictions, Rembrandt presents "
                       "Judith calmly seated at the banquet table, her serene gaze contrasting with the violent "
                       "nature of her act. A servant stands nearby, adding depth, while Rembrandt’s use of light and "
                       "shadow enhances the painting’s tension and mystery. X-ray analysis has revealed changes in "
                       "the composition, hinting at Rembrandt’s evolving vision. This work exemplifies his mastery of "
                       "narrative complexity, emotional depth, and the interplay of morality and power."
    },
    {
        "name": "The Rape of Proserpine",
        "description": "Peter Paul Rubens’ 'The Rape of Proserpine' (c. 1636) vividly captures the dramatic abduction "
                       "of Proserpine by Pluto, who forcefully carries her to the underworld. The painting is filled "
                       "with movement and tension, as Proserpine struggles while being taken into Pluto’s chariot, "
                       "her terror evident in her expression and posture. Rubens’ dynamic brushwork, rich colors, "
                       "and striking contrasts between light and shadow heighten the emotional intensity of the "
                       "scene. His powerful depiction of the human form and masterful use of Baroque drama emphasize "
                       "themes of power, violence, and vulnerability. The work remains a celebrated interpretation of "
                       "classical mythology, showcasing Rubens’ ability to merge storytelling with visual grandeur."
    }
]


def get_all():
    return dataset


def get_dataset_iterator():
    """Allows iteration over the dataset."""
    return iter(dataset)


def find_by_name(name):
    """Find an artifact by its name."""
    return next((artifact for artifact in dataset if artifact["name"].lower() == name.lower()), None)


def list_names():
    """Returns a list of artifact names."""
    return [artifact["name"] for artifact in dataset]
