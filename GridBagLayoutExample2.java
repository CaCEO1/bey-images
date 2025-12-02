import java.awt.*;
import javax.swing.*;

public class GridBagLayoutExample2 extends JFrame {

    public GridBagLayoutExample2() {
        setTitle("GridBagLayout Anchor & Weight Example");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new GridBagLayout());
        setSize(400, 300);
        setLocationRelativeTo(null);
    }

    public void addComponents() {

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);
        gbc.fill = GridBagConstraints.BOTH; // Fill available space by default

        // --- Row 0 ---
        // Left-aligned button with no weight
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.gridwidth = 1;
        gbc.gridheight = 1;
        gbc.weightx = 0.0; // No extra horizontal space
        JButton leftButton = new JButton("Left");
        add(leftButton, gbc);

        // Center-aligned label with weight to push buttons to the sides
        gbc.gridx = 1;
        gbc.gridy = 0;
        gbc.gridwidth = 1;
        gbc.gridheight = 1;
        gbc.weightx = 1.0; // Take up extra horizontal space
        JLabel centerLabel = new JLabel("Center Label (Weight = 1.0)");
        add(centerLabel, gbc);

        // Right-aligned button with no weight
        gbc.gridx = 2;
        gbc.gridy = 0;
        gbc.gridwidth = 1;
        gbc.gridheight = 1;
        gbc.weightx = 0.0;
        JButton rightButton = new JButton("Right");
        add(rightButton, gbc);

        // --- Row 1 ---
        // Top-aligned text area with vertical weight (75% of vertical space)
        gbc.gridx = 0;
        gbc.gridy = 1;
        gbc.gridwidth = 1;
        gbc.gridheight = 1;
        gbc.weightx = 1.0; // Reset horizontal weight
        gbc.weighty = 3.0; // 75% of vertical space (3.0 out of 4.0 total)
        JTextArea topTextArea = new JTextArea("Top Aligned");
        JScrollPane topScrollPane = new JScrollPane(topTextArea);
        add(topScrollPane, gbc);

        // Center-aligned text area with vertical weight (75% of vertical space)
        gbc.gridx = 1;
        gbc.gridy = 1;
        gbc.gridwidth = 1;
        gbc.gridheight = 1;
        gbc.weightx = 1.0;
        gbc.weighty = 3.0; // 75% of vertical space
        JTextArea centerTextArea = new JTextArea("Center Aligned (Weight = 1.0)");
        JScrollPane centerScrollPane = new JScrollPane(centerTextArea);
        add(centerScrollPane, gbc);

        // Bottom-aligned text area with vertical weight (75% of vertical space)
        gbc.gridx = 2;
        gbc.gridy = 1;
        gbc.gridwidth = 1;
        gbc.gridheight = 1;
        gbc.weightx = 1.0;
        gbc.weighty = 3.0; // 75% of vertical space
        JTextArea bottomTextArea = new JTextArea("Bottom Aligned");
        JScrollPane bottomScrollPane = new JScrollPane(bottomTextArea);
        add(bottomScrollPane, gbc);

        // --- Row 2 (NEW) ---
        // Terminal area spanning all columns (25% of vertical space)
        gbc.gridx = 0;
        gbc.gridy = 2;
        gbc.gridwidth = 3;
        gbc.gridheight = 1;
        gbc.weightx = 1.0;
        gbc.weighty = 1.0; // 25% of vertical space (1.0 out of 4.0 total)
        JTextArea terminalArea = new JTextArea("Terminal");
        JScrollPane terminalScrollPane = new JScrollPane(terminalArea);
        add(terminalScrollPane, gbc);

        // --- Row 3 ---
        // Button spanning all columns, centered, no extra weight
        gbc.gridx = 0;
        gbc.gridy = 3;
        gbc.gridwidth = 3;
        gbc.gridheight = 1;
        gbc.weightx = 0.0;
        gbc.weighty = 0.0;
        JButton fullWidthButton = new JButton("Full Width Button");
        add(fullWidthButton, gbc);

    }

    public static void main(String[] args) {
        GridBagLayoutExample2 g = new GridBagLayoutExample2();
        g.addComponents();
        g.setVisible(true);
    }
}
